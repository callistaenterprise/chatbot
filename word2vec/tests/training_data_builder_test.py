import unittest
from app.preprocessing.training_data.training_data_builder import TrainingDataBuilder
from os import path
import logging


class TrainingDataBuilderTest(unittest.TestCase):
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)

    def test_generate_training_data(self):
        dir_name = path.dirname(__file__)
        self.training_data_builder = TrainingDataBuilder(path.join(dir_name, "test_data"))
        training_data = list(self.training_data_builder.training_line_generator())
        self.logger.info(f"Training data: {training_data}")
        self.assertEqual(len(training_data), 2)
