FROM --platform=linux/amd64 nl2repobench/openhands-sdk-fork:930e9b1da

LABEL org.nl2repobench.agent-runtime-image="nl2repobench/openhands-sdk-fork:930e9b1da" org.nl2repobench.agent-runtime-image-id="sha256:70525a5fbee81f4d202b7f7de14857fe78f961ce2ec3995efd1a4850e45c7ea5" org.nl2repobench.agent-dependency-build="pip-index-hash-locked-v1"

RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

COPY candidate-requirements.lock.txt /tmp/candidate-requirements.lock.txt
RUN python -m pip install --no-cache-dir --require-hashes \
  --index-url https://pypi.org/simple \
  -r /tmp/candidate-requirements.lock.txt

RUN test -x /opt/openhands-sdk-venv/bin/python && test -x /usr/bin/curl

WORKDIR /workspace
