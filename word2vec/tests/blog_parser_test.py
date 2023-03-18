import unittest
import logging
from os import path
from app.preprocessing.parsing.blog_parser import BlogParser


class BlogParserTest(unittest.TestCase):
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)

    def test_blog_parser(self):
        dir_name = path.dirname(__file__)
        parser = BlogParser(blog_dir=path.join(dir_name, "test_data/raw"), dry_run=True)
        parsed_blog_lines = parser.parse_blog_file(source_file="unparsed.txt", target_file=None)
        for line in parsed_blog_lines:
            self.logger.info(line)

