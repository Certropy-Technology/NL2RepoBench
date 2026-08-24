FROM --platform=linux/amd64 python@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a

RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates git && rm -rf /var/lib/apt/lists/*

COPY candidate-requirements.lock.txt /tmp/candidate-requirements.lock.txt
RUN python -m pip install --no-cache-dir --require-hashes \
  -r /tmp/candidate-requirements.lock.txt

WORKDIR /workspace
