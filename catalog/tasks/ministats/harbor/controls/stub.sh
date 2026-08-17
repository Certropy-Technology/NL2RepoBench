#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/src/ministats

cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools>=70", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "ministats-bench"
version = "1.0.0"
requires-python = ">=3.10"
dependencies = []
EOF

cat > /workspace/src/ministats/__init__.py <<'EOF'
__version__ = "1.0.0"


def normalize(text: str) -> str:
    raise NotImplementedError


def tokenize(text: str) -> list[str]:
    raise NotImplementedError


def summarize(text: str, top: int = 3) -> dict[str, object]:
    raise NotImplementedError
EOF
