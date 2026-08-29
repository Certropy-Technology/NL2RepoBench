#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/httptools
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"
[project]
name = "httptools"
version = "0.8.0"
EOF
cat > /workspace/httptools/__init__.py <<'EOF'
__version__ = "0.8.0"
class HttpRequestParser:
    def __init__(self, protocol): self.protocol = protocol
class HttpResponseParser(HttpRequestParser): pass
def parse_url(url): return None
EOF
