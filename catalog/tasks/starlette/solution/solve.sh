#!/usr/bin/env bash
set -euo pipefail
test -f /solution/source.tar
test "$(sha256sum /solution/source.tar | cut -d' ' -f1)" = "044f15d81b61b252cca22d4ea0893626dbbbbe56f3400090b304c083cfe71bb5"
rm -rf /workspace/*
tar -xf /solution/source.tar -C /workspace
test -f /workspace/pyproject.toml
test -f /workspace/starlette/__init__.py
