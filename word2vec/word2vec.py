import yaml
from preprocessing import MoviePreparer, DataCleaner, TrainingDataBuilder, BlogPreparer
from cbow import CBOW
from skip_gram import Skipgram
# from d_glove import GloVe
# from glove import Glove


def main():
    config_file = 'config.yaml'
    config_dict = None
    with open(config_file) as config:
        config_dict = yaml.load(config, Loader=yaml.Loader)
    implementation = config_dict['implementation']
    window_size = config_dict['window_size'] # 5
    vector_size = config_dict['vector_size'] # 100
    movie_lines = config_dict['movie_lines'] # 'data/movie_lines.txt'
    movie_conversations = config_dict['movie_conversations'] # 'data/movie_conversations.txt'
    blog_directory = config_dict['blog_directory']
    stop_words = config_dict['stop_words']

    movie_preparer = MoviePreparer(movie_lines, movie_conversations)
    parsed_movie_data = movie_preparer.parse_movie_files()
    movie_preparer = None
    blog_preparer = BlogPreparer(blog_directory)
    parsed_blog_data = blog_preparer.parse_blog_files()
    blog_preparer = None
    print("First step of data preparation finished!")
    data_cleaner = DataCleaner(stop_words)
    cleaned_data = data_cleaner.clean_lines(parsed_movie_data)
    cleaned_data = data_cleaner.clean_lines(parsed_blog_data, append=True)
    data_cleaner = None
    print("Second step of data preparation finished!")
    data_builder = TrainingDataBuilder(cleaned_data, window_size)
    vocab_size = 0
    X_y = None
    if implementation.lower() in ['cbow', 'any']:
        vocab_size, X_y = data_builder.build_cbow_training_data()
        print("Third step in data preparation finished! Vocabulary size: {}".format(vocab_size))
        cbow = CBOW(window_size, vector_size, vocab_size)
        cbow.train_model(X_y=X_y, epochs=10)
        cbow = None
    if implementation.lower() in ['skip-gram', 'any']:
        vocab_size, X_y = data_builder.build_sg_training_data()
        print("Third step in data preparation finished! Vocabulary size: {}".format(vocab_size))
        skip_gram = Skipgram(vector_size, vocab_size)
        skip_gram.train_model(X_y=X_y, epochs=10)
        skip_gram = None
    # elif implementation.lower() in ['glove', 'any']:
        # vocab_size,  = data_builder.build_glove_training_data()
        # print("Third step in data preparation finished!")
        # glove_model = Glove(input_file='data/prepared_data.txt', vocab_size=vocab_size, window=window_size, epoch=3)
        # glove_model.train('data/prepared_data.txt')
    data_builder = None
    print('Finished!')

if __name__ == '__main__':
    main()