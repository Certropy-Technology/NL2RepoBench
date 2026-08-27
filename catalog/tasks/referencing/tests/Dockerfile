FROM --platform=linux/amd64 python:3.13-slim-bookworm@sha256:b6bd71b0dd3811ddbcbc523ec2965fd1e1bcfdf7a20ab24679273d3bee726129

COPY requirements.lock.txt /tmp/requirements.lock.txt
RUN python -m pip install --no-cache-dir --require-hashes \
  --index-url https://pypi.org/simple \
  -r /tmp/requirements.lock.txt

COPY candidate-requirements.lock.txt /tmp/candidate-requirements.lock.txt
RUN python -m pip install   --no-cache-dir   --index-url https://pypi.org/simple   --target /opt/candidate-dependencies/site   --require-hashes   -r /tmp/candidate-requirements.lock.txt

COPY runtime/nl2repobench /usr/local/lib/python3.13/site-packages/nl2repobench
COPY command-plan.json /tests/command-plan.json
COPY --chmod=0555 test.sh /tests/test.sh
COPY --chmod=0500 verifier /tests/verifier


RUN useradd --uid 10001 --create-home candidate   && mkdir -p /tests/private   && chmod -R 0500 /tests/private   && chmod -R 0555 /usr/local/lib/python3.13/site-packages/nl2repobench
WORKDIR /tests
