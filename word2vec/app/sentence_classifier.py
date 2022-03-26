from .preprocessing.training_data.training_data_builder import load_training_data, load_tokenizer
import sys
from os import path
from keras import Input, Model
from keras.layers import Conv1D, MaxPool1D
from keras.layers.core import Dense, Flatten
from keras.layers.embeddings import Embedding
from keras.layers.merge import Concatenate
from codetiming import Timer
import numpy as np
import yaml
import logging


def batch(i_list, j_list, out_list, batch_size):
    for i in range(0, min(len(i_list), len(j_list), len(out_list)), batch_size):
        yield i_list[i: i + batch_size], j_list[i: i + batch_size], out_list[i: i + batch_size]


class SentenceClassifier(object):
    logging.basicConfig(level=logging.INFO)

    def __init__(self, vector_size, vocabulary_size, word_vectors, num_classes):
        dir_name = path.dirname(__file__)
        self.logger = logging.getLogger(__name__)
        self.model_file = path.join(dir_name, "../data/5_models/sentiment_classifier.h5")
        self.vocabulary_size = vocabulary_size
        self.logger = logging.getLogger(__name__)

        bigram_input = Input((2,), dtype='int32')
        trigram_input = Input((3,), dtype='int32')

        trainable_bigram_embedding = Embedding(
            input_dim=vocabulary_size,
            output_dim=vector_size,
            weights=word_vectors,
            input_length=2
        )(bigram_input)

        bigram_embedding = Embedding(
            input_dim=vocabulary_size,
            output_dim=vector_size,
            weights=word_vectors,
            input_length=2,
            trainable=False
        )(bigram_input)

        # Reshape layer to concatenate word vectors to 1D
        # trainable_bigram_flat = Flatten()(trainable_bigram_embedding)
        # untrainable_bigram_flat = Flatten()(untrainable_bigram_embedding)

        trainable_trigram_embedding = Embedding(
            input_dim=vocabulary_size,
            output_dim=vector_size,
            weights=word_vectors,
            input_length=3
        )(trigram_input)

        trigram_embedding = Embedding(
            input_dim=vocabulary_size,
            output_dim=vector_size,
            weights=word_vectors,
            input_length=3,
            trainable=False,
        )(trigram_input)

        # Reshape layer to concatenate word vectors to 1D
        # trainable_trigram_flat = Flatten()(trainable_trigram_embedding)
        # untrainable_trigram_flat = Flatten()(untrainable_trigram_embedding)

        bigram_conv = Conv1D(filters=20,  kernel_size=4, activation="relu")(bigram_embedding)
        bigram_maxpool = MaxPool1D()(bigram_conv)

        trigram_conv = Conv1D(filters=20, kernel_size=4, activation="relu")(trigram_embedding)
        trigram_maxpool = MaxPool1D()(trigram_conv)

        bigram_flatten = Flatten()(bigram_maxpool)
        trigram_flatten = Flatten()(trigram_maxpool)

        concatenate = Concatenate([bigram_flatten, trigram_flatten])

        output = Dense(num_classes, activation="softmax")(concatenate)
        self.model = Model(inputs=[bigram_input, trigram_input], outputs=output)
        # Loss function: categorical cross entropy as we select across many different choices
        self.model.compile(loss="categorical_crossentropy")
        self.model.summary(print_fn=self.logger.info)
        # plot_model(model=self.model, to_file="CBOW model.png", show_shapes=True)
        # Preload word vectors if some training has already been done
        if path.exists(self.model_file):
            self.weights = self.model.load_weights(self.model_file)

    def train_model(self, training_data_file, epochs=3):
        X_y = load_training_data(training_data_file)
        all_bigrams = []
        all_trigrams = []
        all_labels = []
        training_samples = X_y["X"]
        labels = X_y["y"]
        for training_sample, label in zip(training_samples, labels):
            all_bigrams.extend(training_sample[0])
            all_trigrams.extend(training_sample[1])
            all_labels.extend(label)
        batch_size = min(100, len(all_labels))
        timer = Timer(
            name="Sentence classifier training timer",
            text="Epoch training time: {minutes:.2f} minutes",
            logger=self.logger.info,
        )
        for epoch in range(epochs):
            loss = 0.0
            timer.start()
            for bigr_batch, trigr_batch, label_batch in batch(
                    all_bigrams, all_trigrams, all_labels, batch_size
            ):
                loss += self.model.train_on_batch(
                    x=[np.array(bigr_batch, dtype="int32"), np.array(trigr_batch, dtype="int32")], y=np.array(label_batch, dtype="int32")
                )
            timer.stop()
            logging.info("Epoch #{}, loss: {}".format(epoch + 1, loss))
        self.model.save_weights(self.model_file)


def main():
    dir_name = path.dirname(__file__)
    word_vectors_file = sys.argv[1]
    # Real data:
    training_data_file = path.join(
        dir_name, "../data/4_training_data/sentence_classifier/training_data.dat"
    )
    # tokenizer = load_tokenizer(path.join(dir_name, "../data/4_training_data/dictionary.dat"))
    # vocabulary_size = len(tokenizer.word_index) + 1
    config_file = path.join(dir_name, "../config.yaml")
    config_dict = None
    with open(config_file) as config:
        config_dict = yaml.load(config, Loader=yaml.Loader)
    vector_size = config_dict["vector_size"]
    word_vectors_tmp = np.load(path.join(dir_name, f"../data/5_models/{word_vectors_file}"))
    word_vectors = np.reshape(word_vectors_tmp, (len(word_vectors_tmp), vector_size))
    logging.info(f"Shape of word vectors before reshape: {word_vectors_tmp.shape}")
    logging.info(f"Shape of word vectors after reshape: {word_vectors.shape}")
    epochs = config_dict["epochs"]
    num_classes = config_dict["sentence_classes"]
    sentence_class_model = SentenceClassifier(vector_size, len(word_vectors_tmp), word_vectors_tmp, num_classes)
    sentence_class_model.train_model(training_data_file, epochs)


if __name__ == "__main__":
    main()
