import unittest
from os import path
import logging
from app.preprocessing.training_data.sentence_classifier_training_builder import SentenceClassifierTrainingBuilder


class SentenceClassifierTrainingBuilderTest(unittest.TestCase):
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    def test_build_sentence_classifier_train_builder(self):
        dir_name = path.dirname(__file__)
        self.training_data_builder = SentenceClassifierTrainingBuilder(
            source_file=path.join(dir_name, "test_chats/sentence_classifier_msgs.txt"),
            tokenizer_file=path.join(dir_name, "test_dictionary/dictionary.dat"),
            dry_run=True,
        )
        X_y = self.training_data_builder.build_sentence_training_data()
        X = X_y["X"]
        y_ = X_y["y"]
        for training_tuple, y in zip(X, y_):
            bigrams = training_tuple[0]
            trigrams = training_tuple[1]
            self.logger.info(f"Bigrams: {bigrams}")
            self.logger.info(f"Trigrams: {trigrams}")
            self.logger.info(f"Labels: {y}")
            self.logger.info(f"bigrams: {len(bigrams)}, trigrams: {len(trigrams)}, labels: {len(y)}")
            self.assertEqual(len(bigrams), len(trigrams), msg=f"Error! Bigrams and trigrams not same length: bigrams: {len(bigrams)}, trigrams: {len(trigrams)}")
            self.assertEqual(len(trigrams), len(y), msg=f"Error! Labels not same length as training samples: labels: {len(y)}, training samples: {len(trigrams)}")


if __name__ == '__main__':
    unittest.main()
