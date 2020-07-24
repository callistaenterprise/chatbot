import word2vec as w2v
import numpy as np
import importlib

importlib.reload(w2v)

#w2v.data_cleaner('testfile.txt', 'out.txt')
w2v.data_cleaner('movie_lines.txt', 'out.txt')

tokens = w2v.tokenize_file('out.txt')
word_to_id, id_to_word = w2v.mapping(tokens)
X, Y = w2v.generate_training_data(tokens, word_to_id, 3)
#print(X)
print(np.shape(X))
print(np.shape(Y))
vocab_size = len(id_to_word)
m = Y.shape[1]
# turn Y into one hot encoding
Y_one_hot = np.zeros((vocab_size, m))
Y_one_hot[Y.flatten(), np.arange(m)] = 1

paras = w2v.skipgram_model_training(X, Y_one_hot, vocab_size, 50, 0.05, 5000, batch_size=128, parameters=None, print_cost=True)

X_test = np.arange(vocab_size)
X_test = np.expand_dims(X_test, axis=0)
softmax_test, _ = w2v.forward_propagation(X_test, paras)
top_sorted_inds = np.argsort(softmax_test, axis=0)[-4:,:]