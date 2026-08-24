#!/usr/bin/env bash
set -euo pipefail

# Trusted Oracle materializes the private reference implementation. The source
# revision and behavior inventory are recorded in the catalog; the implementation
# is intentionally not copied into the Agent image.
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
cp -a "$SCRIPT_DIR/template/." /workspace/
cd /workspace
npm ci --offline --ignore-scripts --no-audit --no-fund
