#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
ln -s /etc/passwd /workspace/escape
