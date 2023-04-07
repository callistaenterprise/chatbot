from .training_data_builder import TrainingDataBuilder, load_tokenizer, save_training_data
from app.preprocessing.cleaning.data_cleaner import clean_line
import sys
import numpy as np
from os import path
from itertools import chain
import json
import yaml
import logging
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(filename="training.log",
                    filemode='w',
                    format="%(asctime)s [%(levelname)s] %(message)s",
                    level=logging.INFO)


# Check for too short paragraphs (arbitrary "min length": 10 words) and (in order of precedence)
# 1. merge with previous paragraph (if exists) or
# 2. merge with subsequent paragraph (if exist) or
# 3. accept short paragraph
def _restructure_paragraphs(paragraphs):
    paragraphs_restructured = []
    buffer = None
    logging.info(f"Number of paragraphs: {len(paragraphs)}")
    for i, paragraph in enumerate(paragraphs):
        if buffer:
            buffer.extend(paragraph)
            paragraph = buffer
        if len(paragraph) > 10 or i == len(paragraphs)-1:
            paragraphs_restructured.append(paragraph)
            buffer = None
        else:
            if i == 0:
                logging.info(f"First paragraph too short, putting it to buffer")
                buffer = paragraph
            elif i < len(paragraphs) and len(paragraphs_restructured) > 0:
                logging.info(f"Paragraph too short, appending it to previous paragraph")
                paragraphs_restructured[len(paragraphs_restructured) - 1].extend(paragraph)
            else:
                paragraphs_restructured.append(paragraph)
    return paragraphs_restructured


class PVDMClassifierTrainingBuilder(TrainingDataBuilder):

    def __init__(self, source_dir, vector_size, window_size, tokenizer_file):
        super().__init__(source_dir, tokenizer_file)
        dir_name = path.dirname(__file__)
        #self.logger = logging.getLogger(__name__)
        self.vector_size = vector_size
        self.window_size = window_size
        self.doc_to_paragraph_ids = {}
        self._paragraph_id = 0
        if path.exists(tokenizer_file):
            self.tokenizer = load_tokenizer(tokenizer_file)
        else:
            raise RuntimeError("There must be a dictionary file created before we can categorize the docs")
        self.training_data_file = path.join(
            dir_name, "../../../data/4_training_data/doc_classifier/training_data.dat"
        )
        self.doc_to_paragraph_ids_file = path.join(
            dir_name, "../../../data/4_training_data/doc_classifier/doc_to_paragraph_ids.json"
        )

    def _document_to_paragraphs(self, doc):
        paragraphs = []
        with open(doc, "r", encoding="utf-8", errors="ignore") as doc_data:
            # A line in any of the files in data/2_parsed/blogs correspond to a paragraph in the original blog post
            for line in doc_data:
                cleaned_line = clean_line(dirty_line=line, stop_words=['a', 'an', 'are', 'as', 'if', 'is', 'for', 'the',
                                                                       'to'])
                word_ids = super().line_to_word_ids(cleaned_line.strip().split())
                if len(word_ids) > 0:
                    paragraphs.append(word_ids)
        logging.info(f"Before restructuring, {doc} contains paragraphs: {len(paragraphs)}")
        restructured_paragraphs = _restructure_paragraphs(paragraphs)
        logging.info(f"After restructuring, {doc} contains paragraphs: {len(restructured_paragraphs)}")
        return restructured_paragraphs

    def _doc_to_paragraph_ids(self, doc_filename, paragraphs):
        paragraph_ids = list(range(self._paragraph_id, self._paragraph_id + len(paragraphs)))
        self._paragraph_id = self._paragraph_id + len(paragraphs)
        logging.info(f"{doc_filename} contains paragraphs: {paragraph_ids}")
        self.doc_to_paragraph_ids[doc_filename] = paragraph_ids
        return paragraph_ids

    def _build_samples_for_paragraph(self, paragraph, paragraph_id):
        # self.logger.info(f"Paragraph: {paragraph}")
        buffer = np.zeros(self.window_size, dtype=np.intc).tolist()
        buffered_paragraph = list(chain(buffer, paragraph, buffer))
        for focus_word_pos, focus_word_id in enumerate(paragraph):
            if focus_word_id == 0:
                continue
            # We zero-initialize paragraph ID + context word IDs array
            context_word_ids = np.zeros((self.window_size * 2) + 1, dtype=np.int32).tolist()
            context_word_ids[0] = paragraph_id
            # The words (in the "window sized"-list of words) *before* our focus word
            start = focus_word_pos - self.window_size
            # The words (in the "window sized"-list of words) *after* our focus word
            end = focus_word_pos + self.window_size + 1
            context_word_index = 1
            buffered_paragraph_index = focus_word_pos
            for i in range(start, end):
                if i == focus_word_pos:
                    buffered_paragraph_index += 1
                    continue
                context_word_ids[context_word_index] = buffered_paragraph[
                    buffered_paragraph_index
                ]
                context_word_index += 1
                buffered_paragraph_index += 1
            logging.debug("X: {} y: {}", context_word_ids, focus_word_id)
            yield context_word_ids, focus_word_id

    def _save_doc_to_paragraphs(self):
        with open(self.doc_to_paragraph_ids_file, 'w') as fw:
            json.dump(self.doc_to_paragraph_ids, fw)

    def build_training_data(self):
        X_y = dict()
        X = []
        Y = []
        for doc in self.cleaned_files:
            _, doc_filename = path.split(doc)
            doc_paragraphs = self._document_to_paragraphs(doc)
            paragraph_ids = self._doc_to_paragraph_ids(doc_filename, doc_paragraphs)
            for (paragraph_id, paragraph) in zip(paragraph_ids, doc_paragraphs):
                for (x, y) in self._build_samples_for_paragraph(paragraph, paragraph_id):
                    X.append(x)
                    Y.append(y)
        X_y["X"] = X
        X_y["y"] = Y
        logging.info(f"Size X: {len(X)}, size y: {len(Y)}")
        save_training_data(self.training_data_file, X_y)
        self._save_doc_to_paragraphs()


def main():
    dir_name = path.dirname(__file__)
    source_dir = sys.argv[1]
    config_file = path.join(dir_name, "../../../config.yaml")
    config_dict = None
    with open(config_file) as config:
        config_dict = yaml.load(config, Loader=yaml.Loader)
    vector_size = config_dict["vector_size"]
    window_size = config_dict["window_size"]
    tokenizer_file = path.join(dir_name, "../../../", config_dict["dictionary"])
    classifier_training_builder = PVDMClassifierTrainingBuilder(source_dir=source_dir, vector_size=vector_size,
                                                                window_size=window_size, tokenizer_file=tokenizer_file)
    classifier_training_builder.build_training_data()


if __name__ == "__main__":
    main()
