import unittest
from app.preprocessing.training_data.training_data_builder import TrainingDataBuilder
from os import path
import logging


class TrainingDataBuilderTest(unittest.TestCase):

    def test_generate_glove_training_samples(self):
        dir_name = path.dirname(__file__)
        self.training_data_builder = TrainingDataBuilder(
            source_dir=path.join(dir_name, "test_cleaned_train_data.txt"),
            window_size=2,
            dry_run=True)
        vocabulary_size, X_y = self.training_data_builder.build_sg_training_data()
        logging.info("Skip grams: {}", X_y)
        self.assertEqual(vocabulary_size, 11)


if __name__ == "__main__":
    unittest.main()
