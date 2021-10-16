import numpy as np
import pickle
import operator
from os import path
from keras.preprocessing import sequence


class TrainingDataBuilder(object):
	new_line = '\r\n'

	def __init__(self, cleaned_file, window_size):
		dir_name = path.dirname(__file__)
		self.source_file = cleaned_file
		self.vocabulary = set()
		self.word2id_file = path.join(dir_name, '../../data/training_data/word2id.dat')
		self.word2id = self.__load_word_2_id() if path.exists(self.word2id_file) else dict()
		self.id2word_file = path.join(dir_name, '../../data/training_data/id2word.dat')
		self.id2word = self.__load_id_2_word() if path.exists(self.id2word_file) else dict()
		self.window_size = window_size
		self.cbow_training_data_file = path.join(dir_name, '../../data/training_data/cbow_training_data.dat')
		self.sg_training_data_file = path.join(dir_name, '../../data/training_data/sg_training_data.dat')

	def __update_vocabulary(self, line: str):
		words = line.split(' ')
		self.vocabulary.update(words)

	def __update_vocabulary_with_count(self, line: str, word_counter: dict):
		words = line.split(' ')
		self.vocabulary.update(words)
		for word in words:
			if word in word_counter.keys():
				word_counter[word] = word_counter[word] + 1
			else:
				word_counter[word] = 1
		return word_counter

	def __update_dictionaries(self, line, index):
		# When we cannot create a full sample from our training sentences
		# we will pad them so all train samples have same size
		for word in line.split(' '):
			if word not in self.word2id:
				self.word2id[word] = index
				self.id2word[index] = word
				index += 1
		return index

	def line_to_word_ids(self, line):
		word_ids = []
		for word in line.split(' '):
			word_ids.append(self.word2id[word])
		return word_ids

	# Let's define a function for generating training samples from our training sentences
	# This will return a list of training samples based on a particular conversation from our training data
	# Yields a tuple with an array of length window_size*2 of word ids for context words and the id of the focus word
	def __generate_training_samples(self, conversation):
		conversation_len = len(conversation)
		for conversation_index, word_id in enumerate(conversation):
			# The words (in the window sized window of words) before our focus word
			start = conversation_index - self.window_size
			# The words (in the window sized window of words) after our focus word
			end = min(conversation_index + self.window_size + 1, conversation_len)
			context_word_ids = np.zeros(self.window_size * 2)
			context_word_index = 0
			for i in range(start, end):
				if 0 <= i < conversation_len and i != conversation_index:
					context_word_ids[context_word_index] = conversation[i]
					context_word_index += 1

			focus_word = word_id
			yield context_word_ids, focus_word

	def build_cbow_training_data(self):
		if path.exists(self.cbow_training_data_file) and path.exists(self.word2id_file):
			X_y = self.__load_training_data(self.cbow_training_data_file)
			self.word2id = self.__load_word_2_id()
		else:
			X_y = dict()
			X = []
			y = []
			self.word2id['PAD'] = 0
			current_dictionary_index = 1
			with open(self.source_file) as training_data:
				for line in training_data:
					line = line.rstrip(TrainingDataBuilder.new_line)
					self.__update_vocabulary(line)
					current_dictionary_index = self.__update_dictionaries(line, current_dictionary_index)
					word_ids = self.line_to_word_ids(line)
					for context_word_ids, focus_word_id in self.__generate_training_samples(word_ids):
						X.append(context_word_ids)
						y.append(focus_word_id)

			self.__save_id_2_word()
			self.__save_word_2_id()
			self.__save_training_data(self.cbow_training_data_file, X_y)
			# Transform each focus word ID into a one-hot vector
			# THIS CANNOT BE DONE, CAUSES OUT-OF-MEMORY!
			# Y = [np_utils.to_categorical(focus_word, vocabulary_size) for focus_word in y]
			X_y['X'] = X
			X_y['y'] = y

		vocabulary_size = len(self.word2id)
		return vocabulary_size, X_y

	def build_sg_training_data(self):
		X_y = dict()
		if path.exists(self.sg_training_data_file) and path.exists(self.word2id_file):
			X_y = self.__load_training_data(self.sg_training_data_file)
			self.word2id = self.__load_word_2_id()
			vocabulary_size = len(self.word2id)
		else:
			X = []
			self.word2id['PAD'] = 0
			current_dictionary_index = 1
			with open(self.source_file) as training_data:
				for line in training_data:
					line = line.rstrip(TrainingDataBuilder.new_line)
					self.__update_vocabulary(line)
					current_dictionary_index = self.__update_dictionaries(line, current_dictionary_index)
					word_ids = self.line_to_word_ids(line)
					X.append(word_ids)

			self.__save_word_2_id()
			self.__save_id_2_word()
			vocabulary_size = len(self.word2id)
			sampling_table = sequence.make_sampling_table(vocabulary_size)
			training_samples_x = []
			training_samples_y = []
			for word_ids in X:
				word_pairs, labels = sequence.skipgrams(word_ids, vocabulary_size, window_size=self.window_size, sampling_table=sampling_table)
				training_samples_x.extend(word_pairs)
				training_samples_y.extend(labels)
			X_y['X'] = training_samples_x
			X_y['y'] = training_samples_y
			self.__save_training_data(self.sg_training_data_file, X_y)
		return vocabulary_size, X_y

	def build_glove_training_data(self):
		cooccurrance = np.zeros([49396, 49396], dtype="int32")
		word_count = dict()
		current_dictionary_index = 0
		with open(self.source_file) as training_data:
			for line in training_data:
				line = line.rstrip(TrainingDataBuilder.new_line)
				word_count = self.__update_vocabulary_with_count(line, word_count)
				current_dictionary_index = self.__update_dictionaries(line, current_dictionary_index)
				word_ids = self.line_to_word_ids(line)
				for context_word_ids, focus_word_id in self.__generate_training_samples(word_ids):
					for context_word_id in context_word_ids:
						cooccurrance[focus_word_id][int(context_word_id)] += 1

		self.__save_word_2_id()
		sorted_word_count = dict(sorted(word_count.items(), key=operator.itemgetter(1),reverse=True))
		print("Most common words: {}".format(list(sorted_word_count)[:150]))
		sorted_word_count = dict(sorted(word_count.items(), key=operator.itemgetter(1)))
		print("Most rare words: {}".format(list(sorted_word_count)[:100]))
		vocabulary_size = len(self.word2id)
		return vocabulary_size, cooccurrance

	def __save_id_2_word(self):
		with open(self.id2word_file, 'wb') as f:
			pickle.dump(self.id2word, f)
		return self.id2word_file

	def __load_id_2_word(self):
		with open(self.id2word_file, 'rb') as f:
			return pickle.load(f)

	def __save_word_2_id(self):
		with open(self.word2id_file, 'wb') as f:
			pickle.dump(self.word2id, f)

	def __load_word_2_id(self):
		with open(self.word2id_file, 'rb') as f:
			return pickle.load(f)

	def __save_training_data(self, training_data_file, X_y):
		with open(training_data_file, 'wb') as f:
			pickle.dump(X_y, f)

	def __load_training_data(self, training_data_file):
		with open(training_data_file, 'rb') as f:
			return pickle.load(f)