import pickle
import sys
import os
from os import path
import yaml
import logging
from keras.preprocessing.text import Tokenizer


def save_training_data(training_data_file, X_y):
    with open(training_data_file, "wb") as f:
        pickle.dump(X_y, f)


def load_training_data(training_data_file):
    with open(training_data_file, "rb") as f:
        return pickle.load(f)


def cleaned_files(source_dir):
    cleaned_data_files = []
    for root, dirs, files in os.walk(source_dir):
        for name in files:
            cleaned_data_files.append(os.path.join(root, name))
    return cleaned_data_files


def load_tokenizer(tokenizer_file):
    with open(tokenizer_file, "rb") as f:
        return pickle.load(f)


class TrainingDataBuilder(object):
    logging.basicConfig(level=logging.INFO)

    def __init__(self, source_dir, tokenizer_file):
        self.logger = logging.getLogger(__name__)
        self.cleaned_files = cleaned_files(source_dir)
        self.logger.debug(f"source files for training: {self.cleaned_files}")
        if path.exists(tokenizer_file):
            self.tokenizer = load_tokenizer(tokenizer_file)
        else:
            self.tokenizer = Tokenizer(oov_token="UNK")
        self.tokenizer_file = tokenizer_file

    def training_line_generator(self):
        for clean_file in self.cleaned_files:
            with open(
                clean_file, "r", encoding="utf-8", errors="ignore"
            ) as training_data:
                for line in training_data:
                    yield line

    def line_to_word_ids(self, line):
        return self.tokenizer.texts_to_sequences([line])[0]

    def vocabulary_size(self):
        return len(self.tokenizer.word_index) + 1

    def vocabulary(self):
        return self.tokenizer.word_index

    def max_word_count(self):
        return max(self.tokenizer.word_counts.values())

    def _save_tokenizer(self):
        with open(self.tokenizer_file, "wb") as f:
            pickle.dump(self.tokenizer, f)

    def tokenize(self):
        # creates word-2-id dictionary
        if not path.exists(self.tokenizer_file):
            self.tokenizer.fit_on_texts(self.training_line_generator())
            self.logger.info(f"Dictionary size: {len(self.tokenizer.word_index) + 1}")
            self._save_tokenizer()


def main():
    dir_name = path.dirname(__file__)
    source_dir = sys.argv[1]
    config_file = path.join(dir_name, "../../../config.yaml")
    config_dict = None
    with open(config_file) as config:
        config_dict = yaml.load(config, Loader=yaml.Loader)
    tokenizer_file = path.join(dir_name, config_dict["dictionary"])
    training_data_builder = TrainingDataBuilder(source_dir, tokenizer_file)
    training_data_builder.tokenize()


if __name__ == "__main__":
    main()
