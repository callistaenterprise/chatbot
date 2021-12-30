import yaml
from os import path
from app.preprocessing.parsing.blog_parser import BlogParser
from app.preprocessing.parsing.movie_parser import MovieParser
from app.preprocessing.cleaning.data_cleaner import DataCleaner
from preprocessing.blog_encoder import BlogEncoder
from app.preprocessing.training_data.training_data_builder import TrainingDataBuilder
import logging


def main():
    dir_name = path.dirname(__file__)
    config_file = path.join(dir_name, "../config.yaml")
    config_dict = None
    with open(config_file) as config:
        config_dict = yaml.load(config, Loader=yaml.Loader)
    window_size = config_dict["window_size"]
    vector_size = config_dict["vector_size"]
    movie_lines = config_dict["movie_lines"]
    movie_conversations = config_dict["movie_conversations"]
    blog_directory = config_dict["blog_directory"]
    encoded_blogs = config_dict["encoded_blog_directory"]
    stop_words = config_dict["stop_words"]
    pretrained_embeddings = config_dict["pretrained_embeddings"]

    movie_preparer = MovieParser(movie_lines, movie_conversations)
    parsed_movie_data = movie_preparer.parse_movie_files()
    parsed_movie_lines = movie_preparer.parse_movie_lines()
    movie_preparer = None
    blog_preparer = BlogParser(blog_directory)
    parsed_blog_data = blog_preparer.parse_blog_files()
    blog_preparer = None
    logging.info("First step of data preparation finished!")
    data_cleaner = DataCleaner(stop_words)
    cleaned_data = data_cleaner.clean_file(parsed_movie_lines)
    cleaned_data = data_cleaner.clean_file(parsed_blog_data, append=True)
    blog_encoder = BlogEncoder(
        blog_dir=blog_directory,
        target_dir=encoded_blogs,
        word_embeddings_file=pretrained_embeddings,
        stop_words=stop_words,
    )
    blog_encoder.encode_blogs()
    data_cleaner = None
    blog_encoder = None
    logging.info("Second step of data preparation finished!")
    data_builder = TrainingDataBuilder(cleaned_data, window_size)
    logging.info("Finished!")
    data_builder = None


if __name__ == "__main__":
    main()
