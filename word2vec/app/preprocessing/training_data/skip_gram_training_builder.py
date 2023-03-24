from .training_data_builder import TrainingDataBuilder, save_training_data
import sys
from os import path
from keras.preprocessing import sequence
import yaml
import logging


class SkipGramTrainingBuilder(TrainingDataBuilder):
    logging.basicConfig(level=logging.INFO)

    def __init__(self, source_dir, window_size, tokenizer_file, dry_run=False):
        super().__init__(source_dir, tokenizer_file)
        dir_name = path.dirname(__file__)
        self.dry_run = dry_run
        self.window_size = window_size
        self.training_data_file = path.join(
            dir_name, "../../../data/4_training_data/skip_gram/training_data.dat"
        )
        self.logger = logging.getLogger(__name__)

    def build_sg_training_data(self):
        if self.dry_run or not path.exists(self.training_data_file):
            vocabulary_size = super().vocabulary_size()
            X_y = dict()
            training_samples_x = []
            training_samples_y = []
            sampling_table = sequence.make_sampling_table(vocabulary_size + 1)

            for line in super().training_line_generator():
                word_ids = super().line_to_word_ids(line)
                word_pairs, labels = sequence.skipgrams(
                    sequence=word_ids,
                    vocabulary_size=vocabulary_size,
                    window_size=self.window_size,
                    sampling_table=sampling_table,
                )
                training_samples_x.extend(word_pairs)
                training_samples_y.extend(labels)
            self.logger.debug(
                f"Skip-gram training samples: {len(training_samples_x)}, labels: {len(training_samples_y)}"
            )
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
    skip_gram_training_builder = SkipGramTrainingBuilder(
        source_dir, window_size, tokenizer_file, tokenizer_json_file
    )
    skip_gram_training_builder.build_sg_training_data()


if __name__ == "__main__":
    main()
