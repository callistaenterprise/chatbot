import unittest
import logging


class MyTestCase(unittest.TestCase):
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)

    def test_clean(self):

        self.assertEqual(True, False)  # add assertion here
