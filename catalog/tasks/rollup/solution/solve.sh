#!/usr/bin/env bash
set -euo pipefail

rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
mkdir -p /workspace
cp -a /solution/reference/. /workspace/
chmod -R a+rX /workspace
test -f /workspace/package.json
test -f /workspace/dist/wasm-node/bindings_wasm_bg.wasm
