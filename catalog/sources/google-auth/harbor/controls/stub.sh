#!/usr/bin/env bash
# Control: a packaging-only candidate. The distribution installs and the import
# namespaces exist, but every behavior is a stub, so the score must stay low.
set -euo pipefail

mkdir -p /workspace/google/auth /workspace/google/oauth2

cat > /workspace/setup.py <<'PY'
from setuptools import setup

setup(
    name="google-auth",
    version="2.56.3",
    packages=["google", "google.auth", "google.oauth2"],
)
PY

printf '' > /workspace/google/__init__.py
printf '' > /workspace/google/auth/__init__.py
printf '' > /workspace/google/oauth2/__init__.py

for module in _cache _helpers api_key credentials downscoped exceptions jwt transport; do
    printf 'def __getattr__(name):\n    raise NotImplementedError(name)\n' \
        > "/workspace/google/auth/${module}.py"
done
for module in credentials service_account; do
    printf 'def __getattr__(name):\n    raise NotImplementedError(name)\n' \
        > "/workspace/google/oauth2/${module}.py"
done
