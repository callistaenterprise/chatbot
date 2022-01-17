from os import path
from keras import Input, Model
from keras.layers import Conv1D, MaxPool1D
from keras.layers.core import Dense, Reshape, Flatten
from keras.layers.embeddings import Embedding
import yaml
import logging


class SentenceClassifier(object):
    logging.basicConfig(level=logging.INFO)

    def __init__(self, vector_size, vocabulary_size):
        dir_name = path.dirname(__file__)
        self.logger = logging.getLogger(__name__)
        self.model_file = path.join(dir_name, "../data/5_models/sentiment_classifier.h5")
        self.vocabulary_size = vocabulary_size

        bigram_input = Input((2,))
        trigram_input = Input((3,))

        trainable_bigram_embedding = Embedding(
            input_dim=vocabulary_size,
            output_dim=vector_size,
            embeddings_initializer="glorot_uniform",
            input_length=2
        )(bigram_input)

        untrainable_bigram_embedding = Embedding(
            input_dim=vocabulary_size,
            output_dim=vector_size,
            embeddings_initializer="glorot_uniform",
            input_length=2,
            trainable=False
        )(bigram_input)

        # Reshape layer to concatenate word vectors to 1D
        trainable_bigram_flat = Flatten()(trainable_bigram_embedding)
        untrainable_bigram_flat = Flatten()(untrainable_bigram_embedding)

        trainable_trigram_embedding = Embedding(
            input_dim=vocabulary_size,
            output_dim=vector_size,
            embeddings_initializer="glorot_uniform",
            input_length=3
        )(trigram_input)

        untrainable_trigram_embedding = Embedding(
            input_dim=vocabulary_size,
            output_dim=vector_size,
            embeddings_initializer="glorot_uniform",
            input_length=3,
            trainable=False,
        )(trigram_input)

        # Reshape layer to concatenate word vectors to 1D
        trainable_trigram_reshape = Flatten()(trainable_trigram_embedding)
        trainable_trigram_reshape = Flatten()(untrainable_trigram_embedding)

        bigram_conv = Conv1D(kernel_size=25, activation="relu")([trainable_bigram_flat, untrainable_bigram_flat])
        MaxPool1D()


def main():
    dir_name = path.dirname(__file__)
    # Real data:
    training_data_file = path.join(
        dir_name, "../data/4_training_data/sentence_classifier/training_data.dat"
    )
    # Test data:
    # training_data_file = path.join(dir_name, '../tests/test_train_data/glove_test.dat')
    config_file = path.join(dir_name, "../config.yaml")
    config_dict = None
    with open(config_file) as config:
        config_dict = yaml.load(config, Loader=yaml.Loader)
    # test data:
    # vector_size = 3
    epochs = config_dict["epochs"]
    glove_model = Glove(vector_size, 53210)
    # test data:
    # glove_model = Glove(vector_size, 89)
    glove_model.train_model(training_data_file, epochs)


if __name__ == "__main__":
    main()
