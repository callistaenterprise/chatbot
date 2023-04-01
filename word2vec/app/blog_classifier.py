from .preprocessing.training_data.training_data_builder import load_training_data
import numpy as np
from keras import Input, Model
from keras.backend import mean
from keras.layers import Lambda
from keras.layers.core import Dense
from keras.layers.merging import Concatenate
from keras.layers.core.embedding import Embedding
from keras.utils import np_utils
from os import path
from codetiming import Timer
import yaml
import logging


def batch(a_list, b_list, batch_size):
    for i in range(0, min(len(a_list), len(b_list)), batch_size):
        paragraph_ids = [i[0] for i in a_list[i: i + batch_size]]
        context_word_ids = [i[1:] for i in a_list[i: i + batch_size]]
        yield paragraph_ids, context_word_ids, b_list[i: i + batch_size]


class BlogClassifier(object):
    logging.basicConfig(level=logging.INFO)

    def __init__(self, vector_size, vocabulary_size, window_size, word_vectors, num_paragraphs):
        dir_name = path.dirname(__file__)
        self.input_size = window_size * 2
        self.vocab_size = vocabulary_size
        self.model_file = path.join(dir_name, "../data/5_models/pv-dm.h5")
        self.logger = logging.getLogger(__name__)

        # Build the PV-DM model:
        paragraph_id_input = Input((1,), dtype='int32')
        context_words_input = Input(shape=(self.input_size,), dtype='int32')
        paragraph_embedding = Embedding(
            input_dim=num_paragraphs,
            output_dim=vector_size,
            embeddings_initializer="glorot_uniform",
            input_length=1
        )(paragraph_id_input)
        # Embedding layer holds our context word vectors while we process them
        context_words_embedding = Embedding(
            input_dim=self.vocab_size,
            output_dim=vector_size,
            weights=[word_vectors],
            input_length=self.input_size,
            trainable=False
        )(context_words_input)
        all_embeddings = Concatenate(axis=1)([paragraph_embedding, context_words_embedding])
        avg = Lambda(lambda x: mean(x, axis=1))(all_embeddings)
        output = Dense(vocabulary_size, activation="softmax")(avg)
        self.model = Model(inputs=[paragraph_id_input, context_words_input], outputs=output)
        # Loss function: categorical cross entropy as we select across many different choices
        self.model.compile(loss="categorical_crossentropy")
        self.model.summary(print_fn=self.logger.info)
        if path.exists(self.model_file):
            self.weights = self.model.load_weights(self.model_file)

    def train_model(self, training_data, epochs):
        all_X = training_data["X"]
        all_y = training_data["y"]
        batch_size = min(100, len(all_y))
        timer = Timer(
            name="PV-DM training timer",
            text="Epoch training time: {minutes:.2f} minutes",
            logger=self.logger.info,
        )
        for epoch in range(epochs):
            loss = 0.0
            timer.start()
            for paragraph_ids, context_word_ids, focus_word_ids in batch(all_X, all_y, batch_size):
                if len(context_word_ids[0]) != self.input_size or len(context_word_ids) != len(focus_word_ids):
                    logging.error(f"Error! shape paragraph_ids: {np.shape(paragraph_ids)} " +
                                  f"shape context_word_ids: {np.shape(context_word_ids)} " +
                                  f"shape focus_word_ids: {np.shape(focus_word_ids)}")
                    break
                loss += self.model.train_on_batch(
                    x=[np.array(list(paragraph_ids)), np.array(list(context_word_ids))],
                    y=np.array(
                        list(
                            np_utils.to_categorical(focus_word_id, self.vocab_size)
                            for focus_word_id in focus_word_ids
                        )
                    ))
            timer.stop()
            self.logger.info("Epoch #{}, loss: {}".format(epoch + 1, loss))
            paragraph_vectors_file = path.join(path.dirname(__file__), f"../data/5_models/paragraph_embeddings_{epoch}")
            np.save(paragraph_vectors_file, self.model.layers[2].get_weights())
        self.model.save_weights(self.model_file)


def main():
    dir_name = path.dirname(__file__)
    training_data_file = path.join(
        dir_name, "../data/4_training_data/doc_classifier/training_data.dat"
    )
    config_file = path.join(dir_name, "../config.yaml")
    config_dict = None
    with open(config_file) as config:
        config_dict = yaml.load(config, Loader=yaml.Loader)
    window_size = config_dict["window_size"]
    vector_size = config_dict["vector_size"]
    word_vectors_file = config_dict["word_vectors"]
    epochs = config_dict["epochs"]
    word_vectors = np.array(np.load(path.join(dir_name, "../", word_vectors_file), allow_pickle=True))
    X_y = load_training_data(training_data_file)
    blog_classifier = BlogClassifier(vector_size=vector_size, vocabulary_size=len(word_vectors),
                                     window_size=window_size, word_vectors=word_vectors, num_paragraphs=1904)
    blog_classifier.train_model(X_y, epochs)


if __name__ == "__main__":
    main()
