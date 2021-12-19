from os import path
import keras.backend as be
from keras import Input, Model
from keras.layers import Dense, Embedding, Average
from keras.utils import np_utils
import numpy as np
from codetiming import Timer
import logging


def batch(a_list, b_list, batch_size):
    for i in range(0, min(len(a_list), len(b_list)), batch_size):
        yield a_list[i:i + batch_size], b_list[i:i + batch_size]


class CBOW(object):

    def __init__(self, window_size, vector_size, vocabulary_size):
        dir_name = path.dirname(__file__)
        self.window_size = window_size
        self.word_vec_size = vector_size
        self.vocab_size = vocabulary_size
        self.model_file = path.join(dir_name, '../data/5_models/cbow.h5')

        # Neural network to compute word vectors CBOW-style
        context_words_input = Input((self.window_size * 2,))
        # Embedding layer holds our word vectors while we process them
        context_word_embedding = Embedding(input_dim=vocabulary_size, output_dim=vector_size, embeddings_initializer='glorot_uniform', input_length=window_size * 2)
        context_word_graph = context_word_embedding(context_words_input)
        avg = Average()([context_word_graph])
        output = Dense(vocabulary_size, activation='softmax')(avg)
        # A single lambda node computes the mean of all input vectors
        # self.model.add(Lambda(lambda x: be.mean(x, axis=1), output_shape=(vector_size,)))
        # Combine the input vectors to a single average vector
        # self.model.add()
        # A dense output layer that selects the focus-word-to-be by index using softmax
        # self.model.add(Dense(vocabulary_size, activation='softmax'))
        self.model = Model(inputs=[context_words_input], outputs=output)
        # Loss function: categorical cross entropy as we select across many different choices
        self.model.compile(loss='categorical_crossentropy')
        # Preload word vectors if some training has already been done
        if path.exists(self.model_file):
            self.weights = self.model.load_weights(self.model_file)

    def train_model(self, X_y, epochs=3, batch_size=50):
        all_X = X_y['X']
        all_y = X_y['y']
        timer = Timer("CBOW training", text="Epoch training time: {minutes:.2f} minutes", logger=logging.INFO)
        for epoch in range(epochs):
            loss = 0.
            timer.start()
            for x, y in batch(all_X, all_y, batch_size):
                if len(x[0]) != self.window_size * 2 or len(x) != len(y):
                    logging.error("Error! x[0]: {}, len(x): {}, len(y): {}".format(len(x[0]), len(x), len(y)))
                    break
                loss += self.model.train_on_batch(x=np.array(list(x)), y=np.array(list(np_utils.to_categorical(focus_word_id, self.vocab_size) for focus_word_id in y)))
            timer.stop()
            logging.info("Epoch #{}, loss: {}".format(epoch, loss))
        self.model.save_weights(self.model_file)