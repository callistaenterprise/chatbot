clean:
	rm -rf __pycache__
	rm -r data/preprocessing/* || true
	rm -r data/training_data/* || true

install: requirements.txt
	pip install -r requirements.txt

prepare:
	rm -r data/preprocessing/* || mkdir data/preprocessing
	rm -r data/training_data/* || mkdir data/training_data

train: data/movies data/blogs data/preprocessing data/encoded_blogs
	python app/word2vec.py