import unittest
from app.preprocessing.training_data_builder import TrainingDataBuilder
from os import path


class TrainingDataBuilderTest(unittest.TestCase):

    def test_generate_training_samples(self):
        dir_name = path.dirname(__file__)
        self.training_data_builder = TrainingDataBuilder(cleaned_file=path.join(dir_name, 'test_cleaned_train_data.txt'), window_size=2, dry_run=True)
        vocabulary_size, X_y = self.training_data_builder.build_cbow_training_data()
        self.assertEqual(vocabulary_size, 10)


if __name__ == '__main__':
    unittest.main()
