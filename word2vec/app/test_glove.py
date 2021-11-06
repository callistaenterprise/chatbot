import numpy as np
import pickle
from scipy.linalg import svd
from datetime import datetime
from preprocessing.blog_preparer import BlogPreparer
from preprocessing.data_cleaner import DataCleaner


class Glove(object):

    def __init__(self, training_file, vocalbulary_size):
        self.val = 0
        self.glove = dict()
        # self.model = Glove()
        # self.model = glove.Glove(cooccurrance_matrix, vocab_size=vocalbulary_size, d=vector_size, alpha=0.75, x_max=100.0)

    def train_model(self, epochs, X):
        batch_size = 32
        U, sigma, Vt = svd(X)
        for epoch in range(epochs):
            loss = 0.
            epoch_start = datetime.now()
            loss = self.model.train(batch_size=batch_size)
            print("Epoch #{}, running for {}, loss: {}".format(epoch, datetime.now() - epoch_start, loss))

    def load_pretrained_vectors(self, glove_file):
        with open(glove_file, "r", encoding="utf-8") as f:
            for line in f:
                line_values = line.split()
                word = line_values[0]
                word_vector = np.asarray(line_values[1:])
                self.glove[word] = word_vector

    def encode_blogs(self, encoded_blog_dir, blog_preparer: BlogPreparer, data_cleaner: DataCleaner):
        for filename, blog_as_string in blog_preparer.parse_blog_files():
            cleaned_blog = data_cleaner.clean_line(blog_as_string)
            words_in_blog = cleaned_blog.split()
            encoded_blog = np.array([self.glove[blog_word] for blog_word in words_in_blog])
            self.save_encoded_blog(encoded_blog_dir, filename[:filename.index(".md")], encoded_blog)

    def save_encoded_blog(self, dir, filename, data):







