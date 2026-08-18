FROM python:3.12-slim

RUN pip install --no-cache-dir \
    pytest \
    pytest-cov \
    typing_extensions

COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
COPY test /tests/test

RUN chmod +x /tests/test.sh

WORKDIR /tests
