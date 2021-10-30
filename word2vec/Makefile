clean:
	rm -rf __pycache__
	rm -r data/preprocessing/* || true
	rm -r data/training_data/* || true

install: requirements.txt
	pip install -r requirements.txt

prepare: data/movies data/blogs data/preprocessing
	python app/word2vec.py

test: tests
	python -m unittest discover -s tests -p '*_test.py'

black:
	black app
	black tests