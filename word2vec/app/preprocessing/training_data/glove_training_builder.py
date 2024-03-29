from .training_data_builder import TrainingDataBuilder, save_training_data
from os import path
import sys
import math
import yaml
import numpy as np
import logging


class GloveTrainingBuilder(TrainingDataBuilder):
    logging.basicConfig(level=logging.INFO)

    def __init__(self, source_dir, window_size, tokenizer_file, tokenizer_json, dry_run=False):
        super().__init__(source_dir, tokenizer_file, tokenizer_json)
        dir_name = path.dirname(__file__)
        self.dry_run = dry_run
        self.window_size = window_size
        self.training_data_file = path.join(
            dir_name, "../../../data/4_training_data/glove/training_data.dat"
        )
        self.logger = logging.getLogger(__name__)

    def _generate_word_pairs(self, word_ids, min_i, max_i):
        for posI, wordI in enumerate(word_ids):
            # We check word i against the min-max boundary (we are building a _partial_ co-occurrence matrix)
            if wordI < min_i or wordI >= max_i:
                continue
            for posJ, wordJ in enumerate(word_ids):
                # We check if word j is within context window of word i
                if (
                    posI == posJ
                    or posI - self.window_size > posJ
                    or posI + self.window_size < posJ
                ):
                    continue
                yield wordI, wordJ

    def build_glove_training_data(self, batch_size=1000):
        if self.dry_run or not path.exists(self.training_data_file):
            # Step 1: Co-occurrence matrix
            vocabulary_size = super().vocabulary_size()
            X_y = dict()
            training_samples_x = []
            training_samples_y = []
            start_word_id = 1
            batch_size = min(batch_size, vocabulary_size)
            end_word_id = min(vocabulary_size, start_word_id + batch_size)
            batch_counter = 1
            word_count_cap = max(1, math.floor(super().max_word_count() * 0.7))
            self.logger.debug(
                f"Max word count: {super().max_word_count()}, word count cap:{word_count_cap}"
            )
            while end_word_id > start_word_id:
                self.logger.debug(
                    f"Batch#: {batch_counter}, start word id: {start_word_id}, end word id: {end_word_id}"
                )
                partial_co_occurrence_matrix = np.zeros(
                    shape=(batch_size, vocabulary_size), dtype=np.intc
                )
                for line in super().training_line_generator():
                    word_ids = super().line_to_word_ids(line)
                    for word_i_id, word_j_id in self._generate_word_pairs(
                        word_ids, start_word_id, end_word_id
                    ):
                        word_i_index = (word_i_id - 1) % batch_size
                        word_j_index = word_j_id - 1
                        partial_co_occurrence_matrix[word_i_index][word_j_index] += 1
                self.logger.debug(
                    f"prepared partial co-occurrence:\n{partial_co_occurrence_matrix}"
                )
                training_indices = np.nonzero(partial_co_occurrence_matrix)
                training_data = [None] * len(training_indices[0])
                expected_values = [None] * len(training_indices[0])
                self.logger.debug(f"Not null indices: {training_indices}")
                for sample in range(len(training_indices[0])):
                    word_i_index = training_indices[0][sample]
                    word_j_index = training_indices[1][sample]
                    training_data[sample] = [(word_i_index + 1) * batch_counter, word_j_index + 1]
                    co_occurrence = min(
                        word_count_cap,
                        partial_co_occurrence_matrix[word_i_index][word_j_index],
                    )
                    expected_values[sample] = math.log(co_occurrence)
                    self.logger.debug(
                        f"training data: {training_data[sample]} exp: {expected_values[sample]}"
                    )
                training_samples_x.extend(training_data)
                training_samples_y.extend(expected_values)
                batch_counter += 1
                start_word_id = end_word_id
                end_word_id = min(vocabulary_size, end_word_id + batch_size)

            X_y["X"] = training_samples_x
            X_y["y"] = training_samples_y
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
    tokenizer_file = path.join(dir_name, "../../../", config_dict["dictionary"])
    tokenizer_json_file = path.join(dir_name, "../../../", config_dict["dictionary_json"])
    glove_training_builder = GloveTrainingBuilder(
        source_dir, window_size, tokenizer_file, tokenizer_json_file
    )
    glove_training_builder.build_glove_training_data()


if __name__ == "__main__":
    main()
