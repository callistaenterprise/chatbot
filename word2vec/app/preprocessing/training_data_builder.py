import numpy as np
import pickle
import operator
from os import path
from itertools import *
from keras.preprocessing import sequence
from keras.preprocessing.text import Tokenizer


class TrainingDataBuilder(object):
    new_line = "\r\n"

    def __init__(self, cleaned_file, window_size, dry_run=False):
        dir_name = path.dirname(__file__)
        self.source_file = cleaned_file
        self.vocabulary = set()
        self.dry_run = dry_run
        self.window_size = window_size
        self.cbow_training_data_file = path.join(
            dir_name, "../../data/training_data/cbow_training_data.dat"
        )
        self.sg_training_data_file = path.join(
            dir_name, "../../data/training_data/sg_training_data.dat"
        )
        self.glove_training_data_file = path.join(
            dir_name, "../../data/training_data/glove_training_data.dat"
        )
        self.tokenizer = Tokenizer(oov_token='UNK')

    def __test_generator(self):
        with open(self.source_file) as training_data:
            for line in training_data:
                yield line

    def line_to_word_ids(self, line):
        return self.tokenizer.texts_to_sequences(line)

    # Let's define a function for generating training samples from our training sentences
    # This will return a list of training samples based on a particular conversation from our training data
    # Yields a tuple with an array of length window_size*2 of word ids for context words and the id of the focus word
    def __generate_training_samples(self, sample_text):
        buffer = np.zeros(self.window_size, dtype=int).tolist()
        buffered_sampled_text = list(chain(buffer, sample_text, buffer))
        print("buffered_sampled_text: {}".format(buffered_sampled_text))
        # We yield one training sample for each word in sample_text
        for sample_text_pos, focus_word_id in enumerate(sample_text):
            # We zero-initialize context word-ID array
            context_word_ids = np.zeros(self.window_size * 2, dtype=int).tolist()
            # The words (in the "window sized"-list of words) *before* our focus word
            start = sample_text_pos - self.window_size
            # The words (in the "window sized"-list of words) *after* our focus word
            end = sample_text_pos + self.window_size + 1
            context_word_index = 0
            buffered_sampled_text_index = sample_text_pos
            for i in range(start, end):
                if i == sample_text_pos:
                    buffered_sampled_text_index += 1
                    continue
                context_word_ids[context_word_index] = buffered_sampled_text[
                    buffered_sampled_text_index
                ]
                context_word_index += 1
                buffered_sampled_text_index += 1
            print("X: {} y: {}".format(context_word_ids, focus_word_id))
            yield context_word_ids, focus_word_id

    def build_cbow_training_data(self):
        self.tokenizer.fit_on_texts(self.__test_generator())
        if path.exists(self.cbow_training_data_file) and self.dry_run is False:
            X_y = self.__load_training_data(self.cbow_training_data_file)
        else:
            X_y = dict()
            X = []
            y = []
            with open(self.source_file) as training_data:
                for line in training_data:
                    word_ids = self.tokenizer.texts_to_sequences([line])[0]
                    for context_word_ids, focus_word_id in self.__generate_training_samples(word_ids):
                        X.append(context_word_ids)
                        y.append(focus_word_id)

            X_y["X"] = X
            X_y["y"] = y
            if not self.dry_run:
                self.__save_training_data(self.cbow_training_data_file, X_y)

        return len(self.tokenizer.word_index) + 1, X_y

    def build_sg_training_data(self):
        self.tokenizer.fit_on_texts(self.__test_generator())
        vocabulary_size = len(self.tokenizer.word_index) + 1
        if path.exists(self.sg_training_data_file) and self.dry_run is False:
            X_y = self.__load_training_data(self.sg_training_data_file)
        else:
            X_y = dict()
            training_samples_x = []
            training_samples_y = []
            sampling_table = sequence.make_sampling_table(vocabulary_size)
            with open(self.source_file) as training_data:
                for line in training_data:
                    word_ids = self.tokenizer.texts_to_sequences([line])[0]
                    word_pairs, labels = sequence.skipgrams(
                        word_ids,
                        vocabulary_size,
                        window_size=self.window_size,
                        sampling_table=sampling_table,
                    )
                    training_samples_x.extend(word_pairs)
                    training_samples_y.extend(labels)

            X_y["X"] = training_samples_x
            X_y["y"] = training_samples_y
            if not self.dry_run:
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
                current_dictionary_index = self.__update_dictionaries(
                    line, current_dictionary_index
                )
                word_ids = self.line_to_word_ids(line)
                for context_word_ids, focus_word_id in self.__generate_training_samples(
                    word_ids
                ):
                    for context_word_id in context_word_ids:
                        cooccurrance[focus_word_id][int(context_word_id)] += 1

        self.__save_word_2_id()
        sorted_word_count = dict(
            sorted(word_count.items(), key=operator.itemgetter(1), reverse=True)
        )
        print("Most common words: {}".format(list(sorted_word_count)[:150]))
        sorted_word_count = dict(sorted(word_count.items(), key=operator.itemgetter(1)))
        print("Most rare words: {}".format(list(sorted_word_count)[:100]))
        vocabulary_size = len(self.word2id)
        return vocabulary_size, cooccurrance

    def __save_training_data(self, training_data_file, X_y):
        with open(training_data_file, "wb") as f:
            pickle.dump(X_y, f)

    def __load_training_data(self, training_data_file):
        with open(training_data_file, "rb") as f:
            return pickle.load(f)
