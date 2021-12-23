from app.preprocessing.training_data.training_data_builder import TrainingDataBuilder, save_training_data
import sys
from os import path
from keras.preprocessing import sequence
from keras.preprocessing.text import Tokenizer
import yaml
import logging


class SkipGramTrainingBuilder(TrainingDataBuilder):
    NEW_LINE = "\r\n"

    def __init__(self, source_dir, window_size, dry_run=False):
        super().__init__(source_dir)
        dir_name = path.dirname(__file__)
        self.dry_run = dry_run
        self.window_size = window_size
        self.training_data_file = path.join(
            dir_name, "../../../data/4_training_data/skip_gram/training_data.dat"
        )
        self.tokenizer = Tokenizer(oov_token="UNK")

    def build_sg_training_data(self):
        if not path.exists(self.training_data_file):
            self.tokenizer.fit_on_texts(super().training_line_generator())
            vocabulary_size = len(self.tokenizer.word_index) + 1
            X_y = dict()
            training_samples_x = []
            training_samples_y = []
            sampling_table = sequence.make_sampling_table(vocabulary_size)

            for line in super().training_line_generator():
                word_ids = self.tokenizer.texts_to_sequences([line])[0]
                word_pairs, labels = sequence.skipgrams(sequence=word_ids,
                                                        vocabulary_size=vocabulary_size,
                                                        window_size=self.window_size,
                                                        sampling_table=sampling_table,
                                                        )
                training_samples_x.extend(word_pairs)
                training_samples_y.extend(labels)

            X_y["X"] = training_samples_x
            X_y["y"] = training_samples_y
            if self.dry_run:
                return vocabulary_size, X_y
            else:
                save_training_data(self.training_data_file, X_y)
                logging.info(f"Vocabulary size: {vocabulary_size}")


def main():
    dir_name = path.dirname(__file__)
    source_dir = sys.argv[1]
    config_file = path.join(dir_name, "../../../config.yaml")
    config_dict = None
    with open(config_file) as config:
        config_dict = yaml.load(config, Loader=yaml.Loader)
    window_size = config_dict["window_size"]
    skip_gram_training_builder = SkipGramTrainingBuilder(source_dir, window_size)
    skip_gram_training_builder.build_sg_training_data()


if __name__ == "__main__":
    main()