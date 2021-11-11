import yaml
from os import path
from preprocessing.blog_preparer import BlogPreparer
from preprocessing.movie_preparer import MoviePreparer
from preprocessing.data_cleaner import DataCleaner
from preprocessing.training_data_builder import TrainingDataBuilder
import logging


def main():
    dirname = path.dirname(__file__)
    config_file = path.join(dirname, "../config.yaml")
    config_dict = None
    with open(config_file) as config:
        config_dict = yaml.load(config, Loader=yaml.Loader)
    window_size = config_dict["window_size"]
    vector_size = config_dict["vector_size"]
    movie_lines = config_dict["movie_lines"]
    movie_conversations = config_dict["movie_conversations"]
    blog_directory = config_dict["blog_directory"]
    stop_words = config_dict["stop_words"]

    movie_preparer = MoviePreparer(movie_lines, movie_conversations)
    parsed_movie_data = movie_preparer.parse_movie_files()
    parsed_movie_lines = movie_preparer.parse_movie_lines()
    movie_preparer = None
    blog_preparer = BlogPreparer(blog_directory)
    parsed_blog_data = blog_preparer.parse_blog_files()
    blog_preparer = None
    logging.info("First step of data preparation finished!")
    data_cleaner = DataCleaner(stop_words)
    # cleaned_data = data_cleaner.clean_lines(parsed_movie_data)
    cleaned_data = data_cleaner.clean_lines(parsed_movie_lines)
    cleaned_data = data_cleaner.clean_lines(parsed_blog_data, append=True)
    data_cleaner = None
    logging.info("Second step of data preparation finished!")
    data_builder = TrainingDataBuilder(cleaned_data, window_size)
    logging.info("Finished!")
    data_builder = None


if __name__ == "__main__":
    main()
