import numpy as np
from scipy.linalg import svd
from datetime import datetime


class Glove(object):

    def __init__(self, training_file, vocalbulary_size):
        self.val = 0
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
        glove = dict()
        with open(glove_file, "r", encoding="utf-8") as f:
            for line in f:
                line_values = line.split()
                word = line_values[0]
                word_vector = np.asarray(line_values[1:])
                glove[word] = word_vector
        return glove
