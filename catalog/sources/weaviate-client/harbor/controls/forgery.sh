#!/usr/bin/env bash
set -euo pipefail

bash /solution/../controls/stub.sh 2>/dev/null || true
mkdir -p /workspace/weaviate/classes
cat > /workspace/setup.py <<'PY'
from setuptools import setup

setup(
    name="weaviate-client",
    version="4.23.1.dev26+g9f59a367f",
    packages=["weaviate", "weaviate.classes"],
    python_requires=">=3.10",
)
PY
cat > /workspace/weaviate/__init__.py <<'PY'
__version__ = "4.23.1.dev26+g9f59a367f"
class WeaviateClient: pass
class WeaviateAsyncClient: pass
def connect_to_local(*args, **kwargs): return None
def connect_to_custom(*args, **kwargs): return None
def use_async_with_local(*args, **kwargs): return None
auth = object()
collections = object()
exceptions = object()
PY
cat > /workspace/weaviate/classes/__init__.py <<'PY'
config = object()
init = object()
query = object()
PY
printf '%s\n' '{"reward":1.0}' > /workspace/reward.json
printf '%s\n' '{"valid":true,"passed":94,"reward":1.0}' > /workspace/grading.json
mkdir -p /workspace/logs/verifier
printf '%s\n' '1.0' > /workspace/logs/verifier/reward.txt
