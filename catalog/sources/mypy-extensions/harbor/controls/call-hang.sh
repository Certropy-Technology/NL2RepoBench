#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["flit_core>=3.11,<4"]
build-backend = "flit_core.buildapi"

[project]
name = "mypy_extensions"
version = "1.2.0.dev0"
description = "Call timeout control"
EOF
cat > /workspace/mypy_extensions.py <<'EOF'
"""Call timeout control package."""
import time
time.sleep(300)
EOF
