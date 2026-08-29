#!/usr/bin/env bash
set -euo pipefail

rm -rf /tmp/httpx-sse-reference
mkdir -p /tmp/httpx-sse-reference /workspace
tar -xf "$(dirname "$0")/source.tar" -C /tmp/httpx-sse-reference --strip-components=1
cp -a /tmp/httpx-sse-reference/pyproject.toml /workspace/pyproject.toml
cp -a /tmp/httpx-sse-reference/setup.cfg /workspace/setup.cfg
cp -a /tmp/httpx-sse-reference/setup.py /workspace/setup.py
cp -a /tmp/httpx-sse-reference/src /workspace/src
