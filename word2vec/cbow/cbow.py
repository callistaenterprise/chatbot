from os import path
import keras.backend as be
from keras.models import Sequential
from keras.layers import Dense, Embedding, Lambda
from keras.utils import np_utils
from datetime import datetime
import numpy as np


class CBOW(object):

    def __init__(self, window_size, vector_size, vocabulary_size):
        self.window_size = window_size
        self.word_vec_size = vector_size
        self.vocab_size = vocabulary_size

        # Neural network to compute word vectors CBOW-style
        self.model = Sequential()
        # Embedding layer holds our word vectors while we process them
        self.model.add(Embedding(input_dim=vocabulary_size, output_dim=vector_size, input_length=window_size * 2))
        # A single lambda node computes the mean of all input vectors
        self.model.add(Lambda(lambda x: be.mean(x, axis=1), output_shape=(vector_size,)))
        # A dense output layer that selects the focus-word-to-be by index using softmax
        self.model.add(Dense(vocabulary_size, activation='softmax'))
        # Loss function: categorical cross entropy as we select across many different choices
        self.model.compile(loss='categorical_crossentropy', optimizer='rmsprop')
        # Preload word vectors if some training has already been done
        if path.exists('data/cbow.h5'):
            self.weights = self.model.load_weights('data/cbow.h5')

    def __batch(self, a_list, b_list, batch_size):
        for i in range(0, min(len(a_list), len(b_list)), batch_size):
            yield a_list[i:i + batch_size], b_list[i:i + batch_size]

    def train_model(self, X_y=None, epochs=3):
        all_X = X_y['X']
        all_y = X_y['y']
        batch_size = 32
        for epoch in range(epochs):
            loss = 0.
            epoch_start = datetime.now()
            for x, y in self.__batch(all_X, all_y, batch_size):
                if len(x[0]) != self.window_size * 2 or len(x) != len(y):
                    print("Error! x[0]: {}, len(x): {}, len(y): {}".format(len(x[0]), len(x), len(y)))
                    break
                loss += self.model.train_on_batch(x=np.array(list(x)), y=np.array(list(np_utils.to_categorical(focus_word_id, self.vocab_size) for focus_word_id in y)))
            print("Epoch #{}, running for {}, loss: {}".format(epoch, datetime.now() - epoch_start, loss))
        self.model.save_weights('data/cbow.h5')
