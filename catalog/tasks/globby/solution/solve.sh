#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"

rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
tar -xf "$SCRIPT_DIR/source.tar" -C /workspace
rm -rf /workspace/.git /workspace/.github /workspace/node_modules

cat > /workspace/package.json <<'JSON'
{
  "name": "globby",
  "version": "16.2.4",
  "description": "User-friendly glob matching",
  "license": "MIT",
  "type": "module",
  "exports": {
    "types": "./index.d.ts",
    "default": "./index.js"
  },
  "sideEffects": false,
  "engines": {
    "node": ">=20"
  },
  "files": [
    "index.js",
    "index.d.ts",
    "ignore.js",
    "utilities.js"
  ],
  "dependencies": {
    "@sindresorhus/merge-streams": "^4.0.0",
    "fast-glob": "^3.3.3",
    "ignore": "^7.0.5",
    "is-path-inside": "^4.0.0",
    "micromatch": "^4.0.8",
    "slash": "^5.1.0",
    "unicorn-magic": "^0.4.0"
  }
}
JSON
cp "$SCRIPT_DIR/package-lock.json" /workspace/package-lock.json
