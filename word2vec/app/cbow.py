from .preprocessing.training_data.training_data_builder import load_training_data, load_tokenizer
from os import path
import yaml
from keras import Input, Model
from keras.backend import mean
from keras.layers import Lambda
from keras.layers.core import Dense, Reshape
from keras.layers.embeddings import Embedding
from keras.utils import np_utils
from tensorflow.keras.utils import plot_model
import numpy as np
from codetiming import Timer
import logging


def batch(a_list, b_list, batch_size):
    for i in range(0, min(len(a_list), len(b_list)), batch_size):
        yield a_list[i : i + batch_size], b_list[i : i + batch_size]


class CBOW(object):
    logging.basicConfig(level=logging.INFO)

    def __init__(self, window_size, vector_size, vocabulary_size):
        dir_name = path.dirname(__file__)
        self.input_size = window_size * 2
        self.vocab_size = vocabulary_size
        self.model_file = path.join(dir_name, "../data/5_models/cbow.h5")
        self.logger = logging.getLogger(__name__)

        # Neural network to compute word vectors CBOW-style
        context_words_input = Input(shape=(self.input_size, 1))
        # Embedding layer holds our word vectors while we process them
        context_words_embedding = Embedding(
            input_dim=self.vocab_size,
            output_dim=vector_size,
            embeddings_initializer="glorot_uniform",
            input_length=self.input_size,
        )(context_words_input)
        reshape = Reshape((vector_size, self.input_size))(context_words_embedding)
        # A single lambda node computes the mean of all input vectors
        avg = Lambda(lambda x: mean(x, axis=1))(reshape)
        # A dense output layer that selects the focus-word-to-be by index using softmax
        output = Dense(vocabulary_size, activation="softmax")(avg)
        self.model = Model(inputs=context_words_input, outputs=output)
        # Loss function: categorical cross entropy as we select across many different choices
        self.model.compile(loss="categorical_crossentropy")
        self.model.summary(print_fn=self.logger.info)
        # plot_model(model=self.model, to_file="CBOW model.png", show_shapes=True)
        # Preload word vectors if some training has already been done
        if path.exists(self.model_file):
            self.weights = self.model.load_weights(self.model_file)

    def train_model(self, training_data_file, epochs=3):
        X_y = load_training_data(training_data_file)
        all_X = X_y["X"]
        all_y = X_y["y"]
        batch_size = min(100, len(all_y))
        timer = Timer(
            name="CBOW training timer",
            text="Epoch training time: {minutes:.2f} minutes",
            logger=self.logger.info,
        )
        for epoch in range(epochs):
            loss = 0.0
            timer.start()
            for x, y in batch(all_X, all_y, batch_size):
                if len(x[0]) != self.input_size or len(x) != len(y):
                    logging.error(
                        "Error! x[0]: {}, len(x): {}, len(y): {}".format(
                            len(x[0]), len(x), len(y)
                        )
                    )
                    break
                loss += self.model.train_on_batch(
                    x=np.array(list(x)),
                    y=np.array(
                        list(
                            np_utils.to_categorical(focus_word_id, self.vocab_size)
                            for focus_word_id in y
                        )
                    ),
                )
            timer.stop()
            self.logger.info("Epoch #{}, loss: {}".format(epoch + 1, loss))
        self.model.save_weights(self.model_file)


def main():
    dir_name = path.dirname(__file__)
    training_data_file = path.join(
        dir_name, "../data/4_training_data/cbow/training_data.dat"
    )
    tokenizer = load_tokenizer(path.join(dir_name, "../data/4_training_data/dictionary.dat"))
    vocabulary_size = len(tokenizer.word_index) + 1
    config_file = path.join(dir_name, "../config.yaml")
    config_dict = None
    with open(config_file) as config:
        config_dict = yaml.load(config, Loader=yaml.Loader)
    window_size = config_dict["window_size"]
    vector_size = config_dict["vector_size"]
    epochs = config_dict["epochs"]
    cbow_model = CBOW(window_size, vector_size, vocabulary_size)
    cbow_model.train_model(training_data_file, epochs)


if __name__ == "__main__":
    main()
