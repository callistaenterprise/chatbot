import unittest
import logging
from os import path
from app.preprocessing.cleaning.data_cleaner import DataCleaner


class DataCleanerTest(unittest.TestCase):
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)

    def test_clean(self):
        dir_name = path.dirname(__file__)
        cleaner = DataCleaner(source_dir=path.join(dir_name, "test_data/parsed"), target_dir=path.join(dir_name, "test_data/does-not-exist"), dry_run=True)
        cleaned_lines = cleaner.clean_file(path.join(dir_name, "test_data/parsed/uncleaned.txt"))
        for line in cleaned_lines:
            self.logger.debug(line)
