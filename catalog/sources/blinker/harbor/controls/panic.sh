#!/usr/bin/env bash
# Panic: implementation crashes on import or basic usage
set -euo pipefail

mkdir -p /workspace/src/blinker

cat > /workspace/src/blinker/__init__.py << 'PANIC_INIT'
raise SystemExit("Panic!")
PANIC_INIT

cat > /workspace/pyproject.toml << 'PANIC_TOML'
[project]
name = "blinker"
version = "1.9.0"
description = "Panic implementation"

[build-system]
requires = ["flit-core<4"]
build-backend = "flit_core.buildapi"
PANIC_TOML

python -m pip install --no-build-isolation --no-deps --no-index -e /workspace
