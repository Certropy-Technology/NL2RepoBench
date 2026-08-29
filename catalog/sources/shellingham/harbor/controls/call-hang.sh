#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/shellingham
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"
[project]
name = "shellingham"
version = "1.5.4"
EOF
cat > /workspace/shellingham/__init__.py <<'EOF'
import time
def detect_shell(*args, **kwargs):
    while True:
        time.sleep(1)
EOF
