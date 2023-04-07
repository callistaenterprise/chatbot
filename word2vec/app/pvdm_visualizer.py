import sys
from os import path
import numpy as np
import yaml
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.manifold import TSNE
from app.preprocessing.training_data.training_data_builder import load_tokenizer
import matplotlib.pyplot as plt
import plotly.graph_objs as go
from sklearn.decomposition import PCA


class PVDMVisualizer(object):

    def __init__(self, vector_size, paragraph_vectors, blog_to_paragraphs_file, id2word):
        self.vector_size = vector_size
        self.word_vectors = word_vectors
        self.word2id = word2id
        self.id2word = id2word
        self.distance_matrix = euclidean_distances(word_vectors)
        self.three_dim = PCA(random_state=0).fit_transform(self.word_vectors)[:, :3]

    def start(self):
        words = input("Enter blog to visualize: ").rstrip()

        self.visualize_tsne(words)
        self.visualize_pca(words)


def main():
    # word_vectors_file = sys.argv[1]
    dir_name = path.dirname(__file__)
    config_file = path.join(dir_name, "../config.yaml")
    config_dict = None
    with open(config_file) as config:
        config_dict = yaml.load(config, Loader=yaml.Loader)
    vector_size = config_dict["vector_size"]
    #tokenizer = load_tokenizer(path.join(dir_name, "../data/4_training_data/dictionary.dat"))
    #reverse_word_map = dict(map(reversed, tokenizer.word_index.items()))
    word_vectors_tmp = np.load(path.join(dir_name, "../data/5_models/pv-dm.h5"), allow_pickle=True)
    print(f"weights shape: {np.shape(word_vectors_tmp)}")
    #word_vectors = np.reshape(word_vectors_tmp, (len(tokenizer.word_index)+1, vector_size))
    # visualizer = PVDMVisualizer(vector_size, word_vectors, tokenizer.word_index, reverse_word_map)
    # visualizer.start()


if __name__ == "__main__":
    main()