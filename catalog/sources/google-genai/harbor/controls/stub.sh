#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/google/genai
cat > /workspace/setup.py <<'PY'
from setuptools import setup
setup(name="google-genai", version="2.20.0", packages=["google", "google.genai"])
PY
printf '' > /workspace/google/__init__.py
cat > /workspace/google/genai/__init__.py <<'PY'
class Client:
    pass
from . import errors, types
PY
cat > /workspace/google/genai/types.py <<'PY'
class Part: pass
class Content: pass
class UserContent: pass
class ModelContent: pass
class GenerateContentResponse: pass
class HttpOptions: pass
PY
cat > /workspace/google/genai/errors.py <<'PY'
class APIError(Exception): pass
class ClientError(APIError): pass
class ServerError(APIError): pass
PY
for module in _transformers _api_client _common chats pagers; do
  printf 'def __getattr__(name):\n    raise NotImplementedError(name)\n' > "/workspace/google/genai/${module}.py"
done
