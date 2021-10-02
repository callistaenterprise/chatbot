import sys
import numpy as np
from cbow import CBOW
from skip_gram import Skipgram
from preprocessing import TrainingDataBuilder
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt


def main():
    model = sys.argv[1]
    window_size = 3
    vector_size = 64
    word_vectors = None
    data_builder = TrainingDataBuilder('data/training_data/cleaned_data.txt', window_size)

    if model.lower() == 'cbow':
        cbow = CBOW(window_size, vector_size, 49405)
        word_vectors = cbow.model.get_weights()[0]
    elif model.lower() == 'skip-gram':
        skipgram = Skipgram(vector_size, 49405)
        word_vectors = skipgram.model.get_weights()[0]
    distance_matrix = euclidean_distances(word_vectors)
    print(distance_matrix.shape)
    similar_words = {search_term: [data_builder.id2word[idx] for idx in distance_matrix[data_builder.word2id[search_term] - 1].argsort()[1:6] + 1]
                     for search_term in ['little', 'people', 'anything', 'thought', 'weather', 'coffee', 'friend', 'shoes']}
    print(similar_words)
    words = sum([[k] + v for k, v in similar_words.items()], [])
    words_ids = [data_builder.word2id[w] for w in words]
    word_vectors = np.array([word_vectors[idx] for idx in words_ids])
    print('Total words:', len(words), '\tWord Embedding shapes:', word_vectors.shape)

    tsne = TSNE(n_components=2, random_state=0, n_iter=10000, perplexity=3)
    np.set_printoptions(suppress=True)
    T = tsne.fit_transform(word_vectors)
    labels = words

    plt.figure(figsize=(14, 8))
    plt.scatter(T[:, 0], T[:, 1], c='steelblue', edgecolors='k')
    for label, x, y in zip(labels, T[:, 0], T[:, 1]):
        plt.annotate(label, xy=(x + 1, y + 1), xytext=(0, 0), textcoords='offset points')
    plt.show()

if __name__ == '__main__':
    main()