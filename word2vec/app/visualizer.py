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


class Visualizer(object):

    def __init__(self, vector_size, word_vectors, word2id, id2word):
        self.vector_size = vector_size
        self.word_vectors = word_vectors
        self.word2id = word2id
        self.id2word = id2word
        self.distance_matrix = euclidean_distances(word_vectors)
        self.three_dim = PCA(random_state=0).fit_transform(self.word_vectors)[:, :3]

    def start(self):
        words = input("Enter words to visualize: ").rstrip().split(" ")
        self.visualize_tsne(words)
        self.visualize_pca(words)

    def visualize_tsne(self, words):
        # similar_words = {
        #     search_term: [
        #         self.id2word[idx]
        #         for idx in self.distance_matrix[self.word2id[search_term] - 1].argsort()[1:10] + 1]
        #     for search_term in words.split(" ")
        # }
        # words = sum([[k] + v for k, v in similar_words.items()], [])
        words_ids = [self.word2id[w] for w in words]
        selected_word_vectors = np.array([self.word_vectors[idx] for idx in words_ids])
        tsne = TSNE(n_components=2, random_state=0, n_iter=10000, perplexity=3)
        np.set_printoptions(suppress=True)
        T = tsne.fit_transform(selected_word_vectors)
        labels = words

        plt.figure(figsize=(14, 8))
        plt.scatter(T[:, 0], T[:, 1], c="steelblue", edgecolors="k")
        for label, x, y in zip(labels, T[:, 0], T[:, 1]):
            plt.annotate(
                label, xy=(x + 1, y + 1), xytext=(0, 0), textcoords="offset points"
            )
        plt.show()

    def visualize_pca(self, input, topn=5):
        rand_words = np.random.choice(list(self.word2id.keys()), 10)

        data = []
        count = 0

        for i in range(len(rand_words)):
            trace = go.Scatter3d(
                x=self.three_dim[count:count + topn, 0],
                y=self.three_dim[count:count + topn, 1],
                z=self.three_dim[count:count + topn, 2],
                text=rand_words[count:count + topn],
                name=input[i],
                textposition="top center",
                textfont_size=20,
                mode='markers+text',
                marker={
                    'size': 10,
                    'opacity': 0.8,
                    'color': 2
                }
            )
            data.append(trace)
            count = count + topn

            layout = go.Layout(
                margin={'l': 0, 'r': 0, 'b': 0, 't': 0},
                showlegend=True,
                legend=dict(
                    x=1,
                    y=0.5,
                    font=dict(
                        family="Courier New",
                        size=25,
                        color="black"
                    )),
                font=dict(
                    family=" Courier New ",
                    size=15),
                autosize=False,
                width=1000,
                height=1000
            )

            plot_figure = go.Figure(data=data, layout=layout)
            plot_figure.show()


def main():
    word_vectors_file = sys.argv[1]
    dir_name = path.dirname(__file__)
    config_file = path.join(dir_name, "../config.yaml")
    config_dict = None
    with open(config_file) as config:
        config_dict = yaml.load(config, Loader=yaml.Loader)
    vector_size = config_dict["vector_size"]
    tokenizer = load_tokenizer(path.join(dir_name, "../data/4_training_data/dictionary.dat"))
    reverse_word_map = dict(map(reversed, tokenizer.word_index.items()))
    word_vectors_tmp = np.load(path.join(dir_name, f"../data/5_models/{word_vectors_file}"))
    word_vectors = np.reshape(word_vectors_tmp, (len(tokenizer.word_index)+1, vector_size))
    visualizer = Visualizer(vector_size, word_vectors, tokenizer.word_index, reverse_word_map)
    visualizer.start()


if __name__ == "__main__":
    main()
