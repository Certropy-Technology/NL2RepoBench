FROM nl2repobench/openhands-sdk-fork:930e9b1da

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
