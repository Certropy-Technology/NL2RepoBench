FROM --platform=linux/amd64 nl2repobench/openhands-sdk-fork:930e9b1da

LABEL org.nl2repobench.agent-runtime-image="nl2repobench/openhands-sdk-fork:930e9b1da" org.nl2repobench.agent-runtime-image-id="sha256:21f0ba5b3649db3ccc91b1128e5c8c6ffb915d4a8a04faaa11162793099dfac8" org.nl2repobench.agent-dependency-build="pip-index-hash-locked-v1"

RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY candidate-requirements.lock.txt /tmp/candidate-requirements.lock.txt
RUN python -m pip install --no-cache-dir --require-hashes \
  --index-url https://pypi.org/simple \
  -r /tmp/candidate-requirements.lock.txt

RUN test -x /opt/openhands-sdk-venv/bin/python && test -x /usr/bin/curl

WORKDIR /workspace
