from os import path
from keras import Input, Model
from keras.layers import Dot
from keras.layers.embeddings import Embedding
import logging
from codetiming import Timer


def batch(a_list, b_list, batch_size):
    for i in range(0, min(len(a_list), len(b_list)), batch_size):
        yield a_list[i:i + batch_size], b_list[i:i + batch_size]


class Glove(object):
    def __init__(self, vector_size, vocabulary_size):
        dir_name = path.dirname(__file__)
        self.model_file = path.join(dir_name, '../data/5_models/glove.h5')
        self.vocabulary_size = vocabulary_size
        word_pair_input = Input((2,))

        word_pair_embedding = Embedding(input_dim=vocabulary_size, output_dim=vector_size,
                                        embeddings_initializer='glorot_uniform', input_length=2)
        word_pair_input_graph = word_pair_embedding(word_pair_input)

        output = Dot()([word_pair_input_graph])

        self.model = Model(inputs=[word_pair_input], outputs=output)
        self.model.compile(loss='mse')

    def train_model(self, X_y, epochs=3):
        word_pairs = X_y["X"]
        expected_out = X_y["y"]
        batch_size = 100
        timer = Timer("GloVe training", text="Epoch training time: {minutes:.2f} minutes", logger=logging.INFO)
        for epoch in range(epochs):
            loss = 0.
            timer.start()
            for input_batch, output_batch in self.batch(word_pairs, expected_out, batch_size):
                loss += self.model.train_on_batch(input_batch, output_batch)
            timer.stop()
            logging.info("Epoch #{}, loss: {}".format(epoch, loss))
        self.model.save_weights(self.model_file)



