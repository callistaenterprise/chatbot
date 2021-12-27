import unittest
from os import path
import logging
from app.preprocessing.training_data.cbow_training_builder import CbowTrainingBuilder


class CbowTrainingBuilderTest(unittest.TestCase):
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)

    def test_generate_cbow_training_samples(self):
        dir_name = path.dirname(__file__)
        self.training_data_builder = CbowTrainingBuilder(
            source_dir=path.join(dir_name, "test_data"),
            window_size=2,
            dry_run=True)
        vocabulary_size, X_y = self.training_data_builder.build_cbow_training_data()
        self.logger.info(f"CBOW training samples: {X_y}, vocabulary size: {vocabulary_size}")
        self.assertEqual(vocabulary_size, 10)
