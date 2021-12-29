from os import path
from keras import Input, Model
from keras.layers import Dot
from keras.layers.embeddings import Embedding
import logging
import yaml
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


def main():
    dir_name = path.dirname(__file__)
    training_data_file = path.join(dir_name, '../data/4_training_data/glove/training_data.dat')
    config_file = path.join(dir_name, "../config.yaml")
    config_dict = None
    with open(config_file) as config:
        config_dict = yaml.load(config, Loader=yaml.Loader)
    vector_size = config_dict['vector_size']
    epochs = config_dict['epochs']
    glove_model = Glove(vector_size, 53028)
    glove_model.train_model(training_data_file, epochs)


if __name__ == "__main__":
    main()