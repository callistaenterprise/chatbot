import unittest
import logging
from os import path
from app.pvdm_classifier import batch


class BlogClassifierTest(unittest.TestCase):
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)

    def test_batch(self):
        dir_name = path.dirname(__file__)

        # word_vectors = np.array(np.load(path.join(dir_name, "../data/4_training_data/glove_vectors.npy"),
        #                                 allow_pickle=True))
        # classifier = BlogClassifier(vector_size=100, vocabulary_size=400000, window_size=5, word_vectors=word_vectors,
        #                             num_paragraphs=10)
        X = [[0, 12, 34, 54, 23, 6, 365, 23, 87, 23, 87],
             [1, 13, 33, 55, 22, 7, 364, 24, 86, 24, 86],
             [2, 14, 32, 56, 21, 8, 363, 25, 85, 25, 85],
             [3, 15, 31, 57, 20, 9, 362, 26, 84, 26, 84],
             [4, 16, 30, 58, 19, 10, 361, 27, 83, 27, 83],
             [5, 17, 29, 59, 18, 11, 360, 28, 82, 28, 82]]
        Y = [77, 66, 55, 44, 33, 22]
        for paragraph_ids, context_word_ids, focus_word_ids in batch(a_list=X, b_list=Y, batch_size=2):
            self.logger.info(f"\nparagraph_ids:\n{paragraph_ids},\ncontext_word_ids:\n{context_word_ids}\n" +
                             f"focus_word_ids:\n{focus_word_ids}")
        pass
