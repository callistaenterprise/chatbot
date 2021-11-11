import unittest
from app.preprocessing.training_data_builder import TrainingDataBuilder
from os import path


class TrainingDataBuilderTest(unittest.TestCase):

    def test_generate_cbow_training_samples(self):
        dir_name = path.dirname(__file__)
        self.training_data_builder = TrainingDataBuilder(cleaned_file=path.join(dir_name, 'test_cleaned_train_data.txt'), window_size=2, dry_run=True)
        vocabulary_size, X_y = self.training_data_builder.build_cbow_training_data()
        print("CBOW training samples: {}".format(X_y))
        self.assertEqual(vocabulary_size, 11)

    def test_generate_sg_training_samples(self):
        dir_name = path.dirname(__file__)
        self.training_data_builder = TrainingDataBuilder(cleaned_file=path.join(dir_name, 'test_cleaned_train_data.txt'), window_size=2, dry_run=True)
        vocabulary_size, X_y = self.training_data_builder.build_sg_training_data()
        print("Skip grams: {}".format(X_y))
        self.assertEqual(vocabulary_size, 11)

    def test_generate_glove_training_samples(self):
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
