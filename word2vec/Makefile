clean:
	rm -rf __pycache__
	rm -r data/2_parsed/blogs/* || true
	rm -r data/2_parsed/movies/* || true
	rm -r data/3_cleaned/blogs/* || true
	rm -r data/3_cleaned/movies/* || true
	rm data/4_training_data/dictionary* || true
	rm -r data/4_training_data/cbow/* || true
	rm -r data/4_training_data/glove/* || true
	rm -r data/4_training_data/skip_gram/* || true
	rm -r data/4_training_data/sentence_classifier/* || true
	rm -r data/5_models/* || true
	rm data/dictionary* || true

parse_blogs: data/1_raw/blogs
	python -m app.preprocessing.parsing.blog_parser

parse_movies: data/1_raw/movies
	python -m app.preprocessing.parsing.movie_parser

clean_blogs: data/2_parsed/blogs
	python -m app.preprocessing.cleaning.data_cleaner ../../../data/2_parsed/blogs

clean_movies: data/2_parsed/movies
	python -m app.preprocessing.cleaning.data_cleaner ../../../data/2_parsed/movies

tokenize: data/3_cleaned
	python -m app.preprocessing.training_data.training_data_builder data/3_cleaned

prepare_cbow: data/3_cleaned
	python -m app.preprocessing.training_data.cbow_training_builder data/3_cleaned

prepare_skip_gram: data/3_cleaned
	python -m app.preprocessing.training_data.skip_gram_training_builder data/3_cleaned

prepare_glove: data/3_cleaned
	python -m app.preprocessing.training_data.glove_training_builder data/3_cleaned

prepare_sentence_class: data/6_chats/chatmessages.txt
	python -m app.preprocessing.training_data.sentence_classifier_training_builder

train_cbow: data/4_training_data/cbow/training_data.dat
	python -m app.cbow

train_skip_gram: data/4_training_data/skip_gram/training_data.dat
	python -m app.skip_gram

train_glove: data/4_training_data/glove/training_data.dat
	python -m app.glove

pretrained_glove: ../glove.6B/glove.6B.100d.txt data/4_training_data/dictionary.dat
	python -m app.pretrained_glove glove.6B.100d.txt

train_sentence_class: data/4_training_data/sentence_classifier/training_data.dat data/5_models/glove_tokenizer.dat
	python -m app.sentence_classifier

visualize:
	python -m app.visualizer glove_embeddings_29.npy

build_blog_classifier: data/3_cleaned/blogs
	python -m app.blog_classifier data/3_cleaned/blogs

parser_test: tests/test_data/raw/unparsed.txt
	python -m unittest tests/blog_parser_test.py

cleaner_test: tests/test_data/parsed/uncleaned.txt
	python -m unittest tests/data_cleaner_test.py

cbow_test: tests
	python -m unittest tests/cbow_training_builder_test.py

sentence_class_test: tests
	python -m unittest tests/sentence_classifier_train_test.py

test: tests
	python -m unittest discover -s tests -p '*_test.py'

black:
	black app
	black tests