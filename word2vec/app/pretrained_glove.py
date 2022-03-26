from preprocessing.training_data.training_data_builder import load_tokenizer
from os import path
import numpy as np
import logging
import yaml
# from sklearn.metrics.pairwise import euclidean_distances
# from sklearn.manifold import TSNE
# import matplotlib.pyplot as plt


class PretrainedGlove:
    logging.basicConfig(level=logging.INFO)

    def __init__(self, pretrained_vectors_source, tokenizer_file):
        dir_name = path.dirname(__file__)
        self.logger = logging.getLogger(__name__)
        self.source_file = path.join(
            dir_name, "../..", pretrained_vectors_source
        )
        self.model_file = path.join(dir_name, "../data/4_training_data/glove_tokenizer.dat")
        tokenizer_file = path.join(dir_name, "../", tokenizer_file)
        self.tokenizer = load_tokenizer(tokenizer_file)

    def load_pretrained_glove(self):
        glove_model = dict()
        word_index = {"UNK": 1}
        index = 2
        with open(self.source_file, "r") as glove_file:
            for line in glove_file:
                word, word_vec = line.split(maxsplit=1)
                word_vec = np.fromstring(word_vec, dtype=np.float64, sep=" ")
                glove_model[word] = word_vec
                word_index[word] = index
                index += 1
        self.logger.info(f"Parsed {len(glove_model)} pretrained word vectors")

        if not path.exists(self.model_file):
            np.save(self.model_file, glove_model)

    def update_vocabulary(self, new_word_index_dict):
        self.tokenizer.word_index = new_word_index_dict
        self.tokenizer.index_word = {value: key for key, value in new_word_index_dict.items()}


def main():
    dir_name = path.dirname(__file__)
    config_file = path.join(dir_name, "../config.yaml")
    config_dict = None
    with open(config_file) as config:
        config_dict = yaml.load(config, Loader=yaml.Loader)
    pretrained_glove_file = config_dict["pretrained_embeddings"]
    tokenizer_file = config_dict["dictionary"]
    pretrained_glove = PretrainedGlove(pretrained_glove_file, tokenizer_file)
    pretrained_glove.load_pretrained_glove()


if __name__ == "__main__":
    main()
