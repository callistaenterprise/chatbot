from .training_data_builder import load_tokenizer, save_training_data
import sys
from os import path
import yaml
import logging
from itertools import chain
from nltk import ngrams


class SentenceClassifierTrainingBuilder(object):
    logging.basicConfig(level=logging.INFO)

    def __init__(self, source_file, tokenizer_file, dry_run=False):
        dir_name = path.dirname(__file__)
        self.logger = logging.getLogger(__name__)
        self.training_data_file = path.join(
            dir_name, "../../../data/4_training_data/sentence_classifier/training_data.dat"
        )
        self.source_file = source_file
        self.tokenizer = load_tokenizer(tokenizer_file)
        self.dry_run = dry_run

    def _training_line_generator(self):
        with open(
            self.source_file, "r", encoding="utf-8", errors="ignore"
        ) as training_data:
            for line in training_data:
                yield line.split(",")

    def _line_to_word_ids(self, line):
        return self.tokenizer.texts_to_sequences([line])[0]

    def _generate_training_samples(self, word_ids):
        bigrams = []
        trigrams = []
        if len(word_ids) == 1:
            bigrams = [list(chain(word_ids, [0]))]
            trigrams = [list(chain([0], word_ids, [0]))]
        else:
            for bigram in ngrams(word_ids, 2):
                bigrams.append(list(bigram))
            for trigram in ngrams(word_ids, 3):
                trigrams.append(list(trigram))
            trigrams.append(list(chain(word_ids[len(word_ids)-2:], [0])))
        return bigrams, trigrams

    def build_sentence_training_data(self):
        if self.dry_run or not path.exists(self.training_data_file):
            X_y = dict()
            X = []
            y = []
            for line, label in self._training_line_generator():
                self.logger.debug(f"Training data line: {line}")
                word_ids = self._line_to_word_ids(line)
                self.logger.debug(f"Training data word ids: {word_ids}")
                bigrams, trigrams = self._generate_training_samples(word_ids)
                X.append([bigrams, trigrams])
                y.append([label.rstrip()] * len(bigrams))
            X_y["X"] = X
            X_y["y"] = y
            if self.dry_run:
                return X_y
            else:
                save_training_data(self.training_data_file, X_y)


def main():
    dir_name = path.dirname(__file__)
    source_file = sys.argv[1]
    config_file = path.join(dir_name, "../../../config.yaml")
    config_dict = None
    with open(config_file) as config:
        config_dict = yaml.load(config, Loader=yaml.Loader)
    tokenizer_file = path.join(dir_name, config_dict["dictionary"])
    sentence_class_training_builder = SentenceClassifierTrainingBuilder(source_file, tokenizer_file)
    sentence_class_training_builder.build_sentence_training_data()


if __name__ == "__main__":
    main()
