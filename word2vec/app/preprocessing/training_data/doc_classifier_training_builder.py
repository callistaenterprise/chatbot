from .training_data_builder import load_tokenizer, save_training_data
import sys
import numpy as np
from itertools import *
from os import path
import yaml
import logging


def training_line_generator(doc):
    with open(
            doc, "r", encoding="utf-8", errors="ignore"
    ) as training_data:
        for line in training_data:
            yield line


class DocClassifierTrainingBuilder(object):
    logging.basicConfig(level=logging.INFO)

    def __init__(self, source_dir, window_size, tokenizer_file):
        dir_name = path.dirname(__file__)
        self.docs = path.join(dir_name, source_dir)
        self.logger = logging.getLogger(__name__)
        self.window_size = window_size
        if path.exists(tokenizer_file):
            self.tokenizer = load_tokenizer(tokenizer_file)
        else:
            raise RuntimeError("There must be a dictionary file created before we can categorize the docs")
        self.training_data_file = path.join(
            dir_name, "../../../data/4_training_data/doc_classifier/training_data.dat"
        )

    def _generate_training_samples(self, sample_text):
        buffer = np.zeros(self.window_size, dtype=int).tolist()
        buffered_sampled_text = list(chain(buffer, sample_text, buffer))
        # logging.debug("buffered_sampled_text: {}", buffered_sampled_text)
        # We yield one training sample for each word in sample_text
        for sample_text_pos, focus_word_id in enumerate(sample_text):
            # We zero-initialize context word-ID array
            context_word_ids = np.zeros(self.window_size * 2, dtype=int).tolist()
            # The words (in the "window sized"-list of words) *before* our focus word
            start = sample_text_pos - self.window_size
            # The words (in the "window sized"-list of words) *after* our focus word
            end = sample_text_pos + self.window_size + 1
            context_word_index = 0
            buffered_sampled_text_index = sample_text_pos
            for i in range(start, end):
                if i == sample_text_pos:
                    buffered_sampled_text_index += 1
                    continue
                context_word_ids[context_word_index] = buffered_sampled_text[
                    buffered_sampled_text_index
                ]
                context_word_index += 1
                buffered_sampled_text_index += 1
            self.logger.debug("X: {} y: {}", context_word_ids, focus_word_id)
            yield context_word_ids, focus_word_id

    def line_to_word_ids(self, line):
        return self.tokenizer.texts_to_sequences([line])[0]

    def build_training_data(self):
        X_y = dict()
        X = []
        y = []
        for doc in self.docs:
            _, doc_filename = path.split(doc)
            for line in training_line_generator(doc):
                word_ids = self.line_to_word_ids(line)
                for (
                    context_word_ids,
                    focus_word_id,
                ) in self._generate_training_samples(word_ids):
                    X.append(doc_filename, context_word_ids)
                    y.append(focus_word_id)
        X_y["X"] = X
        X_y["y"] = y
        save_training_data(self.training_data_file, X_y)


def main():
    dir_name = path.dirname(__file__)
    source_dir = sys.argv[1]
    config_file = path.join(dir_name, "../../../config.yaml")
    config_dict = None
    with open(config_file) as config:
        config_dict = yaml.load(config, Loader=yaml.Loader)
    window_size = config_dict["window_size"]
    tokenizer_file = path.join(dir_name, config_dict["dictionary"])
    classifier_training_builder = DocClassifierTrainingBuilder(source_dir, window_size, tokenizer_file)
    classifier_training_builder.build_training_data()


if __name__ == "__main__":
    main()
