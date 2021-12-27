clean:
	rm -rf __pycache__
	rm -r data/2_parsed/blogs/* || true
	rm -r data/2_parsed/movies/* || true
	rm -r data/3_cleaned/blogs/* || true
	rm -r data/3_cleaned/movies/* || true
	rm -r data/4_training_data/cbow/* || true
	rm -r data/4_training_data/glove/* || true
	rm -r data/4_training_data/skip_gram/* || true

parse_blogs: data/1_raw/blogs
	python app/preprocessing/parsing/blog_parser.py

parse_movies: data/1_raw/movies
	python app/preprocessing/parsing/movie_parser.py

clean_blogs: data/2_parsed/blogs
	python app/preprocessing/cleaning/data_cleaner.py data/2_parsed/blogs

clean_movies: data/2_parsed/blogs
	python app/preprocessing/cleaning/data_cleaner.py data/2_parsed/movies

prepare_cbow: data/3_cleaned
	python app/preprocessing/training_data/cbow_training_builder.py data/3_cleaned

prepare_skip_gram: data/3_cleaned
	python app/preprocessing/training_data/skip_gram_training_builder.py data/3_cleaned

prepare_glove: data/3_cleaned
	python app/preprocessing/training_data/glove_training_builder.py data/3_cleaned

train_cbow: data/4_training_data/cbow/training_data.dat
    python app/cbow.py

train_skip_gram: data/4_training_data/skip_gram/training_data.dat
    python app/skip_gram.py

train_glove: data/4_training_data/glove/training_data.dat
    python app/glove.py

test: tests
	python -m unittest discover -s tests -p '*_test.py'

black:
	black app
	black tests