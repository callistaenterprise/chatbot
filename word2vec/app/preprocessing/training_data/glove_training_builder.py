from training_data_builder import TrainingDataBuilder, save_training_data
from os import path
import sys
import math
import yaml
from keras.preprocessing.text import Tokenizer
import numpy as np
import logging


class GloveTrainingBuilder(TrainingDataBuilder):
    NEW_LINE = "\r\n"

    def __init__(self, source_dir, window_size, dry_run=False):
        super().__init__(source_dir, window_size, dry_run)
        dir_name = path.dirname(__file__)
        self.dry_run = dry_run
        self.training_data_file = path.join(
            dir_name, "../../../data/4_training_data/glove/training_data.dat"
        )
        self.tokenizer = Tokenizer(oov_token="UNK")

    def _generate_word_pairs(self, word_ids, min, max):
        for posI, wordI in enumerate(word_ids):
            # We check word i against the min-max boundary (we are building a _partial_ co-occurrence matrix)
            if wordI < min or wordI >= max:
                continue
            for posJ, wordJ in enumerate(word_ids):
                # We check if word j is within context window of word i
                if posI == posJ or posI - self.window_size > posJ or posI + self.window_size < posJ:
                    continue
                yield wordI, wordI

    def build_glove_training_data(self, batch_size=1000):
        if not path.exists(self.training_data_file):
            # Step 1: Co-occurrence matrix
            # creates word-to-id, id-to-word mappings, as well as some other nice stuff
            self.tokenizer.fit_on_texts(super().training_line_generator())
            vocabulary_size = len(self.tokenizer.word_index) + 1
            X_y = dict()
            X_y["X"] = np.empty((0, 2), dtype=int)
            X_y["y"] = np.empty((0, 1))
            start = 0
            end = start + batch_size
            batch_counter = 1
            while end < vocabulary_size or start == 0:
                logging.debug(f"Batch#: {batch_counter}, start word id: {start}, end word id: {end}")
                partial_co_occurrence_matrix = np.zeros(shape=(batch_size, vocabulary_size), dtype=int)
                for line in super().training_line_generator():
                    word_ids = self.tokenizer.texts_to_sequences([line])[0]
                    for word_i, word_j in self._generate_word_pairs(word_ids, start, end):
                        word_i_index = word_i % batch_size
                        partial_co_occurrence_matrix[word_i_index][word_j] += 1

                training_indices = np.nonzero(partial_co_occurrence_matrix)
                training_data = np.zeros((len(training_indices[0]), 2), dtype=int)
                expected_values = np.zeros((len(training_indices[0]), 1))

                for sample in range(len(training_indices[0])):
                    word_i_index = training_indices[0][sample]
                    word_j = training_indices[1][sample]
                    training_data[sample][0] = word_i_index * batch_counter
                    training_data[sample][1] = word_j
                    expected_values[sample] = math.log(partial_co_occurrence_matrix[word_i_index][word_j])
                logging.debug(f"X shape: {X_y['X'].shape}, training_data shape: {training_data.shape}")
                logging.debug(f"Y shape: {X_y['y'].shape}, expected_values shape: {expected_values.shape}")
                logging.debug(f"Did we get some word IDs? {training_data[:1]}: {expected_values[0]}")
                X_y["X"] = np.append(X_y["X"], training_data, axis=0)
                X_y["y"] = np.append(X_y["y"], expected_values, axis=0)
                batch_counter += 1
                start = end
                end = min(len(self.tokenizer.word_index), end + batch_size)

            if self.dry_run:
                return vocabulary_size, X_y
            else:
                save_training_data(self.training_data_file, X_y)
                logging.info(f"Vocabulary size: {vocabulary_size}")


def main():
    dir_name = path.dirname(__file__)
    source_dir = sys.argv[1]
    logging.basicConfig(level=logging.DEBUG)
    config_file = path.join(dir_name, "../../../config.yaml")
    config_dict = None
    with open(config_file) as config:
        config_dict = yaml.load(config, Loader=yaml.Loader)
    window_size = config_dict["window_size"]
    glove_training_builder = GloveTrainingBuilder(source_dir, window_size)
    glove_training_builder.build_glove_training_data()


if __name__ == "__main__":
    main()