#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
tar -xf /solution/urllib3-source.tar -C /workspace
cp /solution/urllib3-version.py /workspace/src/urllib3/_version.py
