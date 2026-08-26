FROM nl2repobench/openhands-sdk-fork:930e9b1da

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# The agent image is dependency-neutral; the verifier owns the frozen native closure.
WORKDIR /workspace
