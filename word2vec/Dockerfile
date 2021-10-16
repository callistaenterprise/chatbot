FROM python:3.8-slim-buster as base

FROM base as builder

RUN mkdir /install
WORKDIR /install

COPY requirements.txt /requirements.txt

RUN python -m pip install --upgrade pip
RUN pip3 install --use-deprecated legacy-resolver --install-option="--target=/install" -r /requirements.txt

FROM base

COPY --from=builder /install /usr/local
COPY app /app
COPY data /data
COPY config.yaml /config.yaml

WORKDIR app

CMD ["python", "word2vec.py"]