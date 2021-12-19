import pickle
import os
import logging


def save_training_data(training_data_file, X_y):
    with open(training_data_file, "wb") as f:
        pickle.dump(X_y, f)


def load_training_data(training_data_file):
    with open(training_data_file, "rb") as f:
        return pickle.load(f)


def cleaned_files(source_dir):
    cleaned_data_files = []
    for root, dirs, files in os.walk(source_dir):
        for name in files:
            cleaned_data_files.append(os.path.join(root, name))
    return cleaned_data_files


class TrainingDataBuilder(object):

    def __init__(self, source_dir):
        self.cleaned_files = cleaned_files(source_dir)
        logging.debug(f"source files for training: {self.cleaned_files}")

    def training_line_generator(self):
        for clean_file in self.cleaned_files:
            with open(clean_file, "r", encoding="utf-8", errors="ignore") as training_data:
                for line in training_data:
                    yield line
