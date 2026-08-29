#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
EXPECTED_SHA="cdeeab4b17c4352fc12ea4a907295688c2ce887f4a87c14ff1e4ec020df0f0c9"
test "$(sha256sum "$SCRIPT_DIR/source.tar" | awk '{print $1}')" = "$EXPECTED_SHA"
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
tar -xf "$SCRIPT_DIR/source.tar" -C /workspace --strip-components=1
