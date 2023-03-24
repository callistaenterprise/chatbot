from .training_data_builder import TrainingDataBuilder, load_tokenizer, save_training_data
import sys
import numpy as np
from itertools import chain
from os import path
import json
import yaml
import logging


class DocClassifierTrainingBuilder(TrainingDataBuilder):
    logging.basicConfig(level=logging.INFO)

    def __init__(self, source_dir, paragraph_length, vector_size, window_size, tokenizer_file):
        super().__init__(source_dir, tokenizer_file)
        dir_name = path.dirname(__file__)
        self.logger = logging.getLogger(__name__)
        self.paragraph_length = paragraph_length
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

    def _paragraphize(self, list_of_words):
        for i in range(0, len(list_of_words), self.paragraph_length):
            yield list_of_words[i:i + self.paragraph_length]

    def _document_to_paragraphs(self, doc):
        doc_as_line = ""
        # Let's concatenate all lines in the blog to a single long line, will make it simpler to
        # create specific length segments for training data
        with open(doc, "r", encoding="utf-8", errors="ignore") as doc_data:
            for line in doc_data:
                doc_as_line = doc_as_line + " " + line.strip()
        # With the whole blog as a single line, we can now divide the blog into paragraph_length segments
        words = doc_as_line.split()
        paragraphs = []
        for paragraph in self._paragraphize(words):
            word_ids = super().line_to_word_ids(paragraph)
            paragraphs.append(word_ids)
        return paragraphs

    def _doc_to_paragraph_ids(self, doc_filename, paragraphs):
        paragraph_ids = list(range(self._paragraph_id, self._paragraph_id + len(paragraphs)))
        self._paragraph_id = self._paragraph_id + len(paragraphs)
        self.logger.info(f"{doc_filename} contains paragraphs: {paragraph_ids}")
        self.doc_to_paragraph_ids[doc_filename] = paragraph_ids
        return paragraph_ids

    def _build_samples_for_paragraph(self, paragraph, paragraph_id):
        # self.logger.info(f"Paragraph: {paragraph}")
        buffered_paragraph = np.pad(paragraph, self.paragraph_length)
        for focus_word_pos, focus_word_id in enumerate(paragraph):
            if focus_word_id == 0:
                continue
            # We zero-initialize paragraph ID + context word IDs array
            context_word_ids = np.zeros((self.window_size * 2)+1, dtype=np.int32).tolist()
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
            self.logger.debug("X: {} y: {}", context_word_ids, focus_word_id)
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
        self.logger.info(f"Size X: {len(X)}, size y: {len(Y)}")
        save_training_data(self.training_data_file, X_y)
        self._save_doc_to_paragraphs()


def main():
    dir_name = path.dirname(__file__)
    source_dir = sys.argv[1]
    config_file = path.join(dir_name, "../../../config.yaml")
    config_dict = None
    with open(config_file) as config:
        config_dict = yaml.load(config, Loader=yaml.Loader)
    paragraph_length = config_dict["paragraph_length"]
    vector_size = config_dict["vector_size"]
    window_size = config_dict["window_size"]
    tokenizer_file = path.join(dir_name, "../../../", config_dict["dictionary"])
    classifier_training_builder = DocClassifierTrainingBuilder(source_dir, paragraph_length, vector_size, window_size,
                                                               tokenizer_file)
    classifier_training_builder.build_training_data()


if __name__ == "__main__":
    main()
