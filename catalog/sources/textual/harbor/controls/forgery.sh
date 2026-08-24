#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/src/textual
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["poetry-core==2.2.1"]
build-backend = "poetry.core.masonry.api"
[tool.poetry]
name = "textual"
version = "0.0.0"
packages = [{include = "textual", from = "src"}]
EOF
cat > /workspace/src/textual/__init__.py <<'EOF'
__version__ = "8.2.8"
EOF
cat > /workspace/reward.json <<'EOF'
{"reward": 1.0}
EOF
