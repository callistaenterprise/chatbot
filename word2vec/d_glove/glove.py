from scipy.linalg import svd
from glove import Glove
import numpy as np
from datetime import datetime


class GloVe(object):

    def __init__(self, training_file, vocalbulary_size, vector_size):
        self.model = Glove()
        # self.model = glove.Glove(cooccurrance_matrix, vocab_size=vocalbulary_size, d=vector_size, alpha=0.75, x_max=100.0)
        # U, sigma, Vt = svd(X)


    def train_model(self, epochs):
        batch_size = 32
        for epoch in range(epochs):
            loss = 0.
            epoch_start = datetime.now()
            loss = self.model.train(batch_size=batch_size)
            print("Epoch #{}, running for {}, loss: {}".format(epoch, datetime.now() - epoch_start, loss))
