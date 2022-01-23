from .preprocessing.training_data.training_data_builder import load_training_data, load_tokenizer
from os import path
from keras import Input, Model
from keras.layers import Dot
from keras.layers.core import Dense, Reshape
from keras.layers.embeddings import Embedding
from tensorflow.keras.utils import plot_model
from codetiming import Timer
import logging
import yaml
import numpy as np


def batch(a_list, b_list, c_list, batch_size):
    for i in range(0, min(len(a_list), len(b_list), len(c_list)), batch_size):
        yield a_list[i: i + batch_size], b_list[i: i + batch_size], c_list[
            i: i + batch_size
        ]


class Skipgram(object):
    logging.basicConfig(level=logging.INFO)

    def __init__(self, vector_size, vocabulary_size):
        dir_name = path.dirname(__file__)
        self.logger = logging.getLogger(__name__)

        self.model_file = path.join(dir_name, "../data/5_models/skip_gram.h5")

        focus_input = Input((1,))
        context_input = Input((1,))

        # Slightly more complex model...
        # We have two separate inputs: focus word and a selected context word (can be real or fake)
        focus_word_embedding = Embedding(
            input_dim=vocabulary_size,
            output_dim=vector_size,
            embeddings_initializer="glorot_uniform",
            input_length=1,
        )(focus_input)

        # Reshape layer to remove unnecessary output dimension
        focus_word_graph = Reshape((vector_size, 1))(focus_word_embedding)

        # The second input, the selected context word
        context_word_embedding = Embedding(
            input_dim=vocabulary_size,
            output_dim=vector_size,
            embeddings_initializer="glorot_uniform",
            input_length=1,
            trainable=False,
        )(context_input)
        # Reshape layer to remove unnecessary output dimension
        context_word_graph = Reshape((vector_size, 1))(context_word_embedding)

        # Merge the two input layers by multiplying the vectors
        dot_product = Dot(axes=1)([focus_word_graph, context_word_graph])
        dot_product_reshaped = Reshape((1,))(dot_product)
        # Single node dense layer with sigmoid to declare real of fake label for context word
        output = Dense(1, activation="sigmoid")(dot_product_reshaped)
        self.model = Model(inputs=[focus_input, context_input], outputs=output)
        # Loss function is binary crossentropy as we only determine if real or fake context word
        self.model.compile(loss="binary_crossentropy")
        self.model.summary(print_fn=self.logger.info)
        # plot_model(model=self.model, to_file="Skip-gram model.png", show_shapes=True)
        # Preload word vectors if some training has already been done
        if path.exists(self.model_file):
            self.model.load_weights(self.model_file)

    def train_model(self, training_data_file, epochs=3):
        X_y = load_training_data(training_data_file)
        word_pairs = X_y["X"]
        focus_words, context_words = zip(*word_pairs)
        focus_words = np.array(focus_words, dtype=np.intc)
        context_words = np.array(context_words, dtype=np.intc)
        labels = X_y["y"]
        batch_size = min(100, len(labels))
        timer = Timer(
            name="Skip-gram training timer",
            text="Epoch training time: {minutes:.2f} minutes",
            logger=self.logger.info,
        )
        for epoch in range(epochs):
            loss = 0.0
            timer.start()
            for fw_batch, cw_batch, label_batch in batch(
                focus_words, context_words, labels, batch_size
            ):
                loss += self.model.train_on_batch(
                    x=[np.array(fw_batch), np.array(cw_batch)], y=np.array(label_batch)
                )
            timer.stop()
            logging.info("Epoch #{}, loss: {}".format(epoch + 1, loss))
            trained_embeddings = self.model.layers[2].get_weights()
            self.model.layers[3].set_weights(trained_embeddings)
        self.model.save_weights(self.model_file)


def main():
    dir_name = path.dirname(__file__)
    training_data_file = path.join(
        dir_name, "../data/4_training_data/skip_gram/training_data.dat"
    )
    tokenizer = load_tokenizer(path.join(dir_name, "../data/4_training_data/dictionary.dat"))
    vocabulary_size = len(tokenizer.word_index) + 1
    config_file = path.join(dir_name, "../config.yaml")
    config_dict = None
    with open(config_file) as config:
        config_dict = yaml.load(config, Loader=yaml.Loader)
    vector_size = config_dict["vector_size"]
    epochs = config_dict["epochs"]
    skip_gram_model = Skipgram(vector_size, vocabulary_size)
    skip_gram_model.train_model(training_data_file, epochs)


if __name__ == "__main__":
    main()
