from .preprocessing.training_data.training_data_builder import load_training_data, load_tokenizer
from os import path
from keras import Input, Model
from keras.layers import Conv1D, MaxPool1D
from keras.layers.core import Dense, Reshape, Flatten
from keras.layers.embeddings import Embedding
from codetiming import Timer
import numpy as np
import yaml
import logging


def batch(i_list, j_list, out_list, batch_size):
    for i in range(0, min(len(i_list), len(j_list), len(out_list)), batch_size):
        yield i_list[i: i + batch_size], j_list[i: i + batch_size], out_list[i: i + batch_size]


class SentenceClassifier(object):
    logging.basicConfig(level=logging.INFO)

    def __init__(self, vector_size, vocabulary_size, num_classes):
        dir_name = path.dirname(__file__)
        self.logger = logging.getLogger(__name__)
        self.model_file = path.join(dir_name, "../data/5_models/sentiment_classifier.h5")
        self.vocabulary_size = vocabulary_size
        self.logger = logging.getLogger(__name__)

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
        trainable_trigram_flat = Flatten()(trainable_trigram_embedding)
        untrainable_trigram_flat = Flatten()(untrainable_trigram_embedding)

        bigram_conv = Conv1D(filters=25,  kernel_size=5, activation="relu")([trainable_bigram_flat, untrainable_bigram_flat])
        bigram_maxpool = MaxPool1D()(bigram_conv)

        trigram_conv = Conv1D(filters=25, kernel_size=5, activation="relu")([trainable_trigram_flat, untrainable_trigram_flat])
        trigram_maxpool = MaxPool1D()(trigram_conv)

        output = Dense(num_classes, activation="softmax")(bigram_maxpool, trigram_maxpool)
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
    # Real data:
    training_data_file = path.join(
        dir_name, "../data/4_training_data/sentence_classifier/training_data.dat"
    )
    tokenizer = load_tokenizer(path.join(dir_name, "../data/4_training_data/dictionary.dat"))
    vocabulary_size = len(tokenizer.word_index) + 1
    config_file = path.join(dir_name, "../config.yaml")
    config_dict = None
    with open(config_file) as config:
        config_dict = yaml.load(config, Loader=yaml.Loader)
    vector_size = config_dict["vector_size"]
    epochs = config_dict["epochs"]
    num_classes = config_dict["sentence_classes"]
    sentence_class_model = SentenceClassifier(vector_size, vocabulary_size, num_classes)
    sentence_class_model.train_model(training_data_file, epochs)


if __name__ == "__main__":
    main()
