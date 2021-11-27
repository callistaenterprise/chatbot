from training_data_builder import TrainingDataBuilder
import numpy as np
from itertools import *
from os import path


class CbowTrainingBuilder(TrainingDataBuilder):
    NEW_LINE = "\r\n"

    def __init__(self, cleaned_file, window_size, dry_run=False):
        super().__init__(cleaned_file, window_size)
        dir_name = path.dirname(__file__)
        self.vocabulary = set()
        self.dry_run = dry_run
        self.training_data_file = path.join(
            dir_name, "../../../data/4_training_data/cbow/training_data.dat"
        )

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
        # logging.debug("buffered_sampled_text: {}", buffered_sampled_text)
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
            # logging.debug("X: {} y: {}", context_word_ids, focus_word_id)
            yield context_word_ids, focus_word_id

    def build_cbow_training_data(self):
        self.tokenizer.fit_on_texts(self.__test_generator())
        if path.exists(self.training_data_file) and self.dry_run is False:
            X_y = super().load_training_data(self.training_data_file)
        else:
            X_y = dict()
            X = []
            y = []
            with open(self.source_file) as training_data:
                for line in training_data:
                    word_ids = self.tokenizer.texts_to_sequences([line])[0]
                    for (
                            context_word_ids,
                            focus_word_id,
                    ) in self.__generate_training_samples(word_ids):
                        X.append(context_word_ids)
                        y.append(focus_word_id)

            X_y["X"] = X
            X_y["y"] = y
            if not self.dry_run:
                super().save_training_data(self.training_data_file, X_y)

        return len(self.tokenizer.word_index) + 1, X_y