FROM --platform=linux/amd64 python:3.12-slim-bookworm@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a

COPY requirements.lock.txt /tmp/requirements.lock.txt
RUN python -m pip install --no-cache-dir --require-hashes \
  --index-url https://pypi.org/simple \
  -r /tmp/requirements.lock.txt

COPY candidate-requirements.lock.txt /tmp/candidate-requirements.lock.txt
RUN python -m pip install   --no-cache-dir   --index-url https://pypi.org/simple   --target /opt/candidate-dependencies/site   --require-hashes   -r /tmp/candidate-requirements.lock.txt

COPY runtime/nl2repobench /usr/local/lib/python3.12/site-packages/nl2repobench
COPY command-plan.json /tests/command-plan.json
COPY --chmod=0555 test.sh /tests/test.sh
COPY --chmod=0500 verifier /tests/verifier


RUN useradd --uid 10001 --create-home candidate   && mkdir -p /tests/private   && chmod -R 0500 /tests/private   && chmod -R 0555 /usr/local/lib/python3.12/site-packages/nl2repobench
WORKDIR /tests
