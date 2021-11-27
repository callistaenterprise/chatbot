from training_data_builder import TrainingDataBuilder
from os import path
import operator
import numpy as np
import logging


class GloveTrainingBuilder(TrainingDataBuilder):
    NEW_LINE = "\r\n"

    def __init__(self, source_dir, window_size, dry_run=False):
        super().__init__(source_dir, window_size, dry_run)
        dir_name = path.dirname(__file__)
        self.vocabulary = set()
        self.dry_run = dry_run
        self.training_data_file = path.join(
            dir_name, "../../../data/4_training_data/glove/training_data.dat"
        )

    def build_glove_training_data(self):
        cooccurrance = np.zeros([49396, 49396], dtype="int32")
        word_count = dict()
        current_dictionary_index = 0
        with open(self.source_file) as training_data:
            for line in training_data:
                line = line.rstrip(TrainingDataBuilder.NEW_LINE)
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

        super().__save_word_2_id()
        sorted_word_count = dict(
            sorted(word_count.items(), key=operator.itemgetter(1), reverse=True)
        )
        logging.debug("Most common words: {}", list(sorted_word_count)[:150])
        sorted_word_count = dict(sorted(word_count.items(), key=operator.itemgetter(1)))
        logging.debug("Most rare words: {}", list(sorted_word_count)[:100])
        vocabulary_size = len(self.word2id)
        return vocabulary_size, cooccurrance

    def line_to_word_ids(self, line):
        return self.tokenizer.texts_to_sequences(line)