FROM --platform=linux/amd64 python@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a

RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir annotated-types==0.7.0 editables==0.5 hatchling==1.28.0 packaging==26.0 pathspec==1.0.4 pluggy==1.6.0 pydantic==2.13.4 pydantic-core==2.46.4 python-dotenv==1.2.2 setuptools==80.9.0 trove-classifiers==2026.6.1.19 typing-extensions==4.15.0 typing-inspection==0.4.4 wheel==0.45.1

WORKDIR /workspace
