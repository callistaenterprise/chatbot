import numpy as np
import h5py
from os import path, listdir
import logging
from app.preprocessing.parsing.blog_parser import get_blog_as_string
from app.preprocessing.cleaning.data_cleaner import DataCleaner


def load_embeddings(embeddings_file):
    embeddings = dict()
    with open(embeddings_file, 'r', encoding='UTF-8') as emb:
        for line in emb:
            word_embedding = line.split()
            word = word_embedding[0]
            embedding = np.array(word_embedding[1:], dtype=np.float64)
            embeddings[word] = embedding
    return embeddings


class BlogEncoder(object):

    def __init__(self, blog_dir, target_dir, word_embeddings_file, stop_words):
        dir_name = path.dirname(__file__)
        self.blog_directory = path.join(dir_name, blog_dir)
        self.target_directory = path.join(dir_name, target_dir)
        self.data_cleaner = DataCleaner(stop_words)
        self.word_embeddings = load_embeddings(word_embeddings_file)

    def encode_blogs(self):
        for filename in listdir(self.blog_directory):
            blog_as_string = get_blog_as_string(self.blog_directory, filename)
            cleaned_blog = self.data_cleaner.clean_line(blog_as_string)
            words = cleaned_blog.split()
            encoded_blog = np.array([self.word_embeddings[word] for word in words], dtype=np.float64)
            logging.info("Dimensions of encoded blog {}: {}", filename, encoded_blog.shape)
            encoded_blog_filename = path.splitext(filename) + ".h5"
            with h5py.File(path.join(self.target_directory, encoded_blog_filename), 'w') as h5writer:
                h5writer.create_dataset("blog", data=encoded_blog)




