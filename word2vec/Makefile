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

prepare: data/movies data/blogs data/preprocessing
	python app/word2vec.py

test: tests
	python -m unittest discover -s tests -p '*_test.py'

black:
	black app
	black tests