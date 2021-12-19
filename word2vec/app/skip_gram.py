from os import path
from keras import Input, Model
from keras.layers import Dot
from keras.layers.core import Dense, Reshape
from keras.layers.embeddings import Embedding
from codetiming import Timer
import logging
import numpy as np


class Skipgram(object):

    def __init__(self, vector_size, vocabulary_size):
        dir_name = path.dirname(__file__)
        self.model_file = path.join(dir_name, '../data/5_models/skip_gram.h5')

        focus_input = Input((1,))
        context_input = Input((1,))

        # Slightly more complex model...
        # We have two separate inputs: focus word and a selected context word (can be real or fake)
        focus_word_embedding = Embedding(input_dim=vocabulary_size, output_dim=vector_size,
                                         embeddings_initializer='glorot_uniform', input_length=1)
        focus_word_graph = focus_word_embedding(focus_input)
        # Reshape layer to remove unnecessary output dimension
        focus_word_graph = Reshape((vector_size, 1))(focus_word_graph)

        # The second input, the selected context word
        context_word_embedding = Embedding(input_dim=vocabulary_size, output_dim=vector_size,
                                           embeddings_initializer='glorot_uniform', input_length=1)
        context_word_graph = context_word_embedding(context_input)
        # Reshape layer to remove unnecessary output dimension
        context_word_graph = Reshape((vector_size, 1))(context_word_graph)

        # Merge the two input layers by multiplying the vectors
        dot_product = Dot(axes=1)([focus_word_graph, context_word_graph])
        # dot_product = Reshape((1,))(dot_product)
        # Single node dense layer with sigmoid to declare real of fake label for context word
        output = Dense(1, activation='sigmoid')(dot_product)
        self.model = Model(inputs=[focus_input, context_input], outputs=output)
        # Loss function is binary crossentropy as we only determine if real or fake context word
        self.model.compile(loss='binary_crossentropy')
        # Preload word vectors if some training has already been done
        if path.exists(self.model_file):
            self.model.load_weights(self.model_file)

    def _batch(self, a_list, b_list, c_list, batch_size):
        for i in range(0, min(len(a_list), len(b_list), len(c_list)), batch_size):
            yield a_list[i:i + batch_size], b_list[i:i + batch_size], c_list[i:i + batch_size]

    def train_model(self, X_y, epochs=3):
        word_pairs = X_y['X']
        focus_words, context_words = zip(*word_pairs)
        focus_words = np.array(focus_words, dtype="int32")
        context_words = np.array(context_words, dtype="int32")
        labels = X_y['y']
        batch_size = 32
        timer = Timer("Skip-gram training", text="Epoch training time: {minutes:.2f} minutes", logger=logging.INFO)
        for epoch in range(epochs):
            loss = 0.
            timer.start()
            for fw_batch, cw_batch, label_batch in self._batch(focus_words, context_words, labels, batch_size):
                loss += self.model.train_on_batch([np.array(fw_batch), np.array(cw_batch)], np.array(label_batch))
            timer.stop()
            logging.info("Epoch #{}, loss: {}".format(epoch, loss))
        self.model.save_weights(self.model_file)
