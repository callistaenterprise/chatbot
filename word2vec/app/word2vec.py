import os
import yaml
from preprocessing.blog_preparer import BlogPreparer
from preprocessing.movie_preparer import MoviePreparer
from preprocessing.data_cleaner import DataCleaner
from preprocessing.training_data_builder import TrainingDataBuilder
from test_glove import Glove


def main():
    dir_name = os.path.dirname(__file__)
    config_file = os.path.join(dir_name, '../config.yaml')
    config_dict = None
    with open(config_file) as config:
        config_dict = yaml.load(config, Loader=yaml.Loader)
    window_size = config_dict['window_size']
    vector_size = config_dict['vector_size']
    movie_lines = config_dict['movie_lines']
    movie_conversations = config_dict['movie_conversations']
    blog_directory = config_dict['blog_directory']
    stop_words = config_dict['stop_words']
    glove_file = config_dict['glove_vectors']

    movie_preparer = MoviePreparer(movie_lines, movie_conversations)
    parsed_movie_data = movie_preparer.parse_movie_files()
    movie_preparer = None
    blog_preparer = BlogPreparer(blog_directory)
    parsed_blog_data = blog_preparer.prepare_blog_training_data()
    # blog_preparer = None
    print("First step of data preparation finished!")
    data_cleaner = DataCleaner(stop_words)
    cleaned_data = data_cleaner.clean_lines(parsed_movie_data)
    cleaned_data = data_cleaner.clean_lines(parsed_blog_data, append=True)
    # data_cleaner = None
    print("Second step of data preparation finished!")
    data_builder = TrainingDataBuilder(cleaned_data, window_size)
    vocab_size, co_occurance = data_builder.build_training_data()

    glove_model = Glove(vocab_size=vocab_size, window=window_size, epoch=3)
    glove_model.load_pretrained_vectors(glove_file)
    glove_model.encode_blogs(blog_dir=blog_directory)
    # glove_model.train('data/prepared_data.txt')
    print('Finished!')
    data_builder = None


if __name__ == '__main__':
    main()