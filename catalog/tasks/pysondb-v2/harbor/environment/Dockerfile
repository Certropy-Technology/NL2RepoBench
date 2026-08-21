FROM --platform=linux/amd64 python@sha256:fc1d7d6e1df26c603b5729e92fff684a56e9d1b8c6db263c6169a1f250e80787

RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
