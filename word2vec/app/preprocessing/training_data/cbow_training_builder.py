from .training_data_builder import TrainingDataBuilder, save_training_data
import sys
import numpy as np
from itertools import *
from os import path
import yaml
import logging


class CbowTrainingBuilder(TrainingDataBuilder):
    logging.basicConfig(level=logging.DEBUG)

    def __init__(self, source_dir, window_size, tokenizer_file, dry_run=False):
        super().__init__(source_dir, tokenizer_file)
        dir_name = path.dirname(__file__)
        self.logger = logging.getLogger(__name__)
        self.window_size = window_size
        self.dry_run = dry_run
        self.training_data_file = path.join(
            dir_name, "../../../data/4_training_data/cbow/training_data.dat"
        )

    # Let's define a function for generating training samples from our training sentences
    # This will return a list of training samples based on a particular conversation from our training data
    # Yields a tuple with an array of length window_size*2 of word ids for context words and the id of the focus word
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
            # logging.debug("X: {} y: {}", context_word_ids, focus_word_id)
            yield context_word_ids, focus_word_id

    def build_cbow_training_data(self):
        if self.dry_run or not path.exists(self.training_data_file):
            X_y = dict()
            X = []
            y = []

            for line in super().training_line_generator():
                self.logger.debug(f"Training data line: {line}")
                word_ids = super().line_to_word_ids(line)
                self.logger.debug(f"Training data word ids: {word_ids}")
                for (
                        context_word_ids,
                        focus_word_id,
                ) in self._generate_training_samples(word_ids):
                    X.append(context_word_ids)
                    y.append(focus_word_id)

            X_y["X"] = X
            X_y["y"] = y
            vocabulary_size = super().vocabulary_size()
            if self.dry_run:
                return vocabulary_size, X_y
            else:
                save_training_data(self.training_data_file, X_y)
                self.logger.info(f"Vocabulary size: {vocabulary_size}")


def main():
    dir_name = path.dirname(__file__)
    source_dir = sys.argv[1]
    config_file = path.join(dir_name, "../../../config.yaml")
    config_dict = None
    with open(config_file) as config:
        config_dict = yaml.load(config, Loader=yaml.Loader)
    window_size = config_dict["window_size"]
    tokenizer_file = path.join(dir_name, config_dict['dictionary'])
    cbow_training_builder = CbowTrainingBuilder(source_dir, window_size, tokenizer_file)
    cbow_training_builder.build_cbow_training_data()


if __name__ == "__main__":
    main()