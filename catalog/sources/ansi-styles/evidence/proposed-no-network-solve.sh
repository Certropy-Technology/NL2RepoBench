#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ORACLE_DIR="$SCRIPT_DIR/oracle-package"
test -f "$ORACLE_DIR/package.json"
test "$(node -p 'JSON.parse(require("fs").readFileSync(process.argv[1])).name' "$ORACLE_DIR/package.json")" = "ansi-styles"
test "$(node -p 'JSON.parse(require("fs").readFileSync(process.argv[1])).version' "$ORACLE_DIR/package.json")" = "7.0.0"
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cp "$ORACLE_DIR/index.js" /workspace/index.js
cp "$ORACLE_DIR/index.d.ts" /workspace/index.d.ts
cp "$ORACLE_DIR/license" /workspace/license
cp "$ORACLE_DIR/readme.md" /workspace/readme.md
cp "$ORACLE_DIR/package.json" /workspace/package.json
cp "$ORACLE_DIR/package-lock.json" /workspace/package-lock.json
