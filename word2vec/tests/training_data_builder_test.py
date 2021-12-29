import unittest
from app.preprocessing.training_data.training_data_builder import TrainingDataBuilder
from os import path
import logging


class TrainingDataBuilderTest(unittest.TestCase):
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)

    def test_generate_training_data(self):
        dir_name = path.dirname(__file__)
        self.training_data_builder = TrainingDataBuilder(source_dir=path.join(dir_name, "test_data"),
                                                         tokenizer_file=path.join(dir_name,
                                                                                  "test_dictionary/dictionary.dat"))
        self.training_data_builder.tokenize()
        self.logger.info(f"Training data: {self.training_data_builder.vocabulary()}")
        self.assertEqual(88, self.training_data_builder.vocabulary_size())
