FROM --platform=linux/amd64 python@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a

RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir setuptools==80.10.2 wheel==0.45.1 pytest==8.3.5 iniconfig==2.0.0 packaging==24.2 pluggy==1.5.0

WORKDIR /workspace
