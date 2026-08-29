#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/rfc3986
cat > /workspace/setup.py <<'PY'
import setuptools
setuptools.setup(name="rfc3986", version="2.0.0", packages=["rfc3986"])
PY
cat > /workspace/rfc3986/__init__.py <<'PY'
import urllib.request
try:
    urllib.request.urlopen("http://example.invalid", timeout=1)
except Exception:
    pass
PY
