FROM --platform=linux/amd64 python@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a

RUN apt-get update && apt-get install -y --no-install-recommends build-essential=12.12 git=1:2.47.3-0+deb13u1 pkg-config=1.8.1-4 libxml2-dev=2.12.7+dfsg+really2.9.14-2.1+deb13u3 libxslt1-dev=1.1.35-1.2+deb13u3 zlib1g-dev=1:1.3.dfsg+really1.3.1-1+b1 && rm -rf /var/lib/apt/lists/*

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
