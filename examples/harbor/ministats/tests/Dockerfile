FROM python:3.12-slim

RUN python -m pip install --no-cache-dir \
    pytest==8.4.1 \
    setuptools==75.8.0 \
    wheel==0.45.1

COPY --chmod=755 test.sh /tests/test.sh
COPY grade.py test_ministats.py /tests/

WORKDIR /tests
