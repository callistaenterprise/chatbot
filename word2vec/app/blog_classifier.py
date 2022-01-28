from .preprocessing.training_data.training_data_builder import load_tokenizer, cleaned_files
import sys
import numpy as np
from itertools import *
from os import path
import yaml
import logging


class BlogClassifier(object):
    logging.basicConfig(level=logging.INFO)

    def __init__(self, source_dir, tokenizer, paragraph_length):
        dir_name = path.dirname(__file__)
        self.logger = logging.getLogger(__name__)
        self.blog_vector_file = path.join(dir_name, "../data/5_models/blog_vectors.dat")
        self.blog_files = cleaned_files(source_dir)
        self.tokenizer = load_tokenizer(tokenizer_file=tokenizer)
        self.paragraph_length = paragraph_length
        stop_words_file = path.join(self.dir_name, "blog_stop_words.txt")
        with open(stop_words_file, "r") as f:
            self.stop_words = [word for line in f for word in line.split()]

    def build_blog_vectors(self):
        pass



def main():
    dir_name = path.dirname(__file__)
    source_dir = sys.argv[1]
    config_file = path.join(dir_name, "../../../config.yaml")
    config_dict = None
    with open(config_file) as config:
        config_dict = yaml.load(config, Loader=yaml.Loader)
    paragraph_length = config_dict["paragraph_length"]
    tokenizer_file = path.join(dir_name, config_dict["dictionary"])

if __name__ == "__main__":
    main()
