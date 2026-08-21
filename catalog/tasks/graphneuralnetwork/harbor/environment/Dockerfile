FROM --platform=linux/amd64 python@sha256:73b4a7f050901a4b6fda237789721ad9deb5d11e437c7122611bb2141385f4ac

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        build-essential \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# The agent image is dependency-neutral; the verifier owns the frozen native closure.
WORKDIR /workspace
