# Doc classifier does not need to be trained, just avg paragraphs!

# from .training_data_builder import load_tokenizer, save_training_data
# import sys
# import numpy as np
# from itertools import *
# from os import path
# import yaml
# import logging
#
#
# def training_line_generator(doc):
#     with open(
#             doc, "r", encoding="utf-8", errors="ignore"
#     ) as training_data:
#         for line in training_data:
#             yield line
#
#
# class DocClassifierTrainingBuilder(object):
#     logging.basicConfig(level=logging.INFO)
#
#     def __init__(self, source_dir, paragraph_length, tokenizer_file):
#         dir_name = path.dirname(__file__)
#         self.docs = path.join(dir_name, source_dir)
#         self.logger = logging.getLogger(__name__)
#         self.paragraph_length = paragraph_length
#         if path.exists(tokenizer_file):
#             self.tokenizer = load_tokenizer(tokenizer_file)
#         else:
#             raise RuntimeError("There must be a dictionary file created before we can categorize the docs")
#         self.training_data_file = path.join(
#             dir_name, "../../../data/4_training_data/doc_classifier/training_data.dat"
#         )
#
#     def _generate_training_samples(self, sample_text):
#         buffer = np.zeros(self.paragraph_length, dtype=int).tolist()
#
#
#     def line_to_word_ids(self, line):
#         return self.tokenizer.texts_to_sequences([line])[0]
#
#     def build_training_data(self):
#         X_y = dict()
#         X = []
#         y = []
#         for doc in self.docs:
#             _, doc_filename = path.split(doc)
#             with open(doc, "r", encoding="utf-8", errors="ignore") as blog_data:
#                 for line in blog_data:
#
#             for line in training_line_generator(doc):
#                 word_ids = self.line_to_word_ids(line)
#                 for (
#                     context_word_ids,
#                     focus_word_id,
#                 ) in self._generate_training_samples(word_ids):
#                     X.append(doc_filename, context_word_ids)
#                     y.append(focus_word_id)
#         X_y["X"] = X
#         X_y["y"] = y
#         save_training_data(self.training_data_file, X_y)
#
#
# def main():
#     dir_name = path.dirname(__file__)
#     source_dir = sys.argv[1]
#     config_file = path.join(dir_name, "../../../config.yaml")
#     config_dict = None
#     with open(config_file) as config:
#         config_dict = yaml.load(config, Loader=yaml.Loader)
#     paragraph_length = config_dict["paragraph_length"]
#     tokenizer_file = path.join(dir_name, config_dict["dictionary"])
#     classifier_training_builder = DocClassifierTrainingBuilder(source_dir, paragraph_length, tokenizer_file)
#     classifier_training_builder.build_training_data()
#
#
# if __name__ == "__main__":
#     main()
