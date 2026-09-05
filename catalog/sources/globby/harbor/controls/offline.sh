#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +

cat > /workspace/package.json <<'JSON'
{
  "name": "globby-offline-control",
  "version": "0.0.0",
  "type": "module",
  "exports": "./index.js"
}
JSON

cat > /workspace/package-lock.json <<'JSON'
{
  "name": "globby-offline-control",
  "version": "0.0.0",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": {
      "name": "globby-offline-control",
      "version": "0.0.0",
      "type": "module"
    }
  }
}
JSON

cat > /workspace/index.js <<'JS'
await fetch('https://example.invalid/nl2repobench-network-must-be-blocked');
export default () => [];
JS
