import unittest
from os import path
import logging
import pickle
from app.preprocessing.training_data.glove_training_builder import GloveTrainingBuilder


class GloveTrainingBuilderTest(unittest.TestCase):
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)

    def test_generate_glove_training_samples(self):
        dir_name = path.dirname(__file__)
        self.training_data_builder = GloveTrainingBuilder(
            source_dir=path.join(dir_name, "test_data"),
            window_size=2,
            tokenizer_file=path.join(dir_name, "test_data/training/dictionary.dat"),
            tokenizer_json=None,
            dry_run=True,
        )
        super(GloveTrainingBuilder, self.training_data_builder).tokenize()
        vocabulary_size, X_y = self.training_data_builder.build_glove_training_data()
        self.logger.info(f"Word pairs: {X_y}")
        # with open(path.join(dir_name, "test_train_data/glove_test.dat"), "wb") as f:
        #     pickle.dump(X_y, f)
        self.assertEqual(89, vocabulary_size)
