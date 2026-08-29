#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/langchain/agents
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "langchain"
version = "0.0.0"
EOF
cat > /workspace/langchain/__init__.py <<'EOF'
EOF
cat > /workspace/langchain/agents/__init__.py <<'EOF'
EOF
cat > /workspace/langchain/agents/structured_output.py <<'EOF'
import time
time.sleep(300)
EOF
