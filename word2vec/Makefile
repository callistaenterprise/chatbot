clean:
	rm -rf __pycache__
	rm -r data/preprocessing/* || true
	rm -r data/training_data/* || true

install: requirements.txt
	pip install -r requirements.txt

prepare: data/movies data/blogs data/preprocessing
	python word2vec.py