#!/usr/bin/env bash
set -euo pipefail
template="$(dirname "$0")/template"
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
cp -a "$template/." /workspace/
chmod -R u+rwX,go+rX /workspace
