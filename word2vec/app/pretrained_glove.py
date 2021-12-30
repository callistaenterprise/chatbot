import sys
from os import path
import numpy as np
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt


class PretrainedGlove:
    def __init__(self, pretrained_vectors_source):
        dir_name = path.dirname(__file__)
        self.source_file = path.join(
            dir_name, "../../glove.6B", pretrained_vectors_source
        )
        self.model_file = path.join(dir_name, "../data/5_models/glove_pretrained.h5")
        self.glove_model = dict()

    def load_pretrained_glove(self):
        with open(self.source_file, "r") as glove_file:
            for line in glove_file:
                split_line = line.split()
                word = split_line[0]
                embedding = np.array(split_line[1:], dtype=np.float64)
                self.glove_model[word] = embedding

    def visualize_vectors(self):
        distance_matrix = euclidean_distances(self.glove_model.values())
        while True:
            user_input = sys.stdin.read()
            if not len(user_input):
                break
            words = user_input.split()
            similar_words = {
                search_term: [
                    data_builder.id2word[idx]
                    for idx in distance_matrix[
                        data_builder.word2id[search_term] - 1
                    ].argsort()[1:6]
                    + 1
                ]
                for search_term in words
            }
            print(similar_words)


def main():
    pretrained_glove = PretrainedGlove(sys.argv[1])
    pretrained_glove.load_pretrained_glove()


if __name__ == "__main__":
    main()
