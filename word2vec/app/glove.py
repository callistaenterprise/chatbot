from .preprocessing.training_data.training_data_builder import load_training_data
from os import path
from keras import Input, Model
from keras.layers import Dot
from keras.layers.core import Reshape
from keras.layers.embeddings import Embedding
from tensorflow.keras.utils import plot_model
import logging
import yaml
from codetiming import Timer
import numpy as np


def batch(a_list, b_list, batch_size):
    for i in range(0, min(len(a_list), len(b_list)), batch_size):
        yield a_list[i : i + batch_size], b_list[i : i + batch_size]


class Glove(object):
    logging.basicConfig(level=logging.INFO)

    def __init__(self, vector_size, vocabulary_size):
        dir_name = path.dirname(__file__)
        self.logger = logging.getLogger(__name__)
        self.model_file = path.join(dir_name, "../data/5_models/glove.h5")
        self.vocabulary_size = vocabulary_size

        word_i_input = Input((1,))
        word_j_input = Input((1,))

        word_i_embedding = Embedding(
            input_dim=vocabulary_size,
            output_dim=vector_size,
            embeddings_initializer="glorot_uniform",
            input_length=1,
        )(word_i_input)

        # Reshape layer to remove unnecessary output dimension
        word_i_graph = Reshape((vector_size, 1))(word_i_embedding)

        word_j_embedding = Embedding(
            input_dim=vocabulary_size,
            output_dim=vector_size,
            embeddings_initializer="glorot_uniform",
            input_length=1,
        )(word_j_input)
        # Reshape layer to remove unnecessary output dimension
        word_j_graph = Reshape((vector_size, 1))(word_j_embedding)

        # Merge the two input layers by multiplying the vectors
        dot_product = Dot(axes=1)([word_i_graph, word_j_graph])
        output = Reshape((1,))(dot_product)

        self.model = Model(inputs=[word_i_input, word_j_input], outputs=output)
        # Loss function is mean squared error from a predicted co-occurrence likelihood value
        self.model.compile(loss="mse", metrics="accuracy")

        self.model.summary(print_fn=self.logger.info)
        plot_model(model=self.model, to_file="Glove model.png", show_shapes=True)
        # Preload word vectors if some training has already been done
        if path.exists(self.model_file):
            self.model.load_weights(self.model_file)

    def train_model(self, training_data_file, epochs=3):
        X_y = load_training_data(training_data_file)
        word_pairs = X_y["X"]
        i_words, j_words = zip(*word_pairs)
        i_words = np.array(i_words, dtype="int32")
        j_words = np.array(j_words, dtype="int32")
        expected_out = X_y["y"]
        batch_size = min(100, len(expected_out))
        timer = Timer(
            name="GloVe training timer",
            text="Epoch training time: {minutes:.2f} minutes",
            logger=self.logger.info,
        )
        for epoch in range(epochs):
            loss = 0.0
            timer.start()
            for fw_batch, cw_batch, expect_out_batch in batch(
                    i_words, j_words, expected_out, batch_size
            ):
                loss += self.model.train_on_batch(
                    [np.array(fw_batch), np.array(cw_batch)], np.array(expect_out_batch)
                )
            timer.stop()
            logging.info("Epoch #{}, loss: {}".format(epoch + 1, loss))
        self.model.save_weights(self.model_file)


def main():
    dir_name = path.dirname(__file__)
    # Real data:
    training_data_file = path.join(
        dir_name, "../data/4_training_data/glove/training_data.dat"
    )
    # Test data:
    # training_data_file = path.join(dir_name, '../tests/test_train_data/glove_test.dat')
    config_file = path.join(dir_name, "../config.yaml")
    config_dict = None
    with open(config_file) as config:
        config_dict = yaml.load(config, Loader=yaml.Loader)
    vector_size = config_dict["vector_size"]
    # test data:
    # vector_size = 3
    epochs = config_dict["epochs"]
    glove_model = Glove(vector_size, 53210)
    # test data:
    # glove_model = Glove(vector_size, 89)
    glove_model.train_model(training_data_file, epochs)


if __name__ == "__main__":
    main()
