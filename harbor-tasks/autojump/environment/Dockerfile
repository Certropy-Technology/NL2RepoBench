FROM --platform=linux/amd64 python@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a

RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates git && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir iniconfig==2.3.0 mock==5.2.0 packaging==26.3 pluggy==1.6.0 pygments==2.21.0 pytest==8.4.1 setuptools==80.10.2 wheel==0.45.1

WORKDIR /workspace
