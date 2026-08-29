#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/lib
cat > /workspace/package.json <<'JSON'
{
  "name": "fs-extra",
  "version": "11.4.0",
  "main": "./lib/index.js",
  "files": ["lib/"],
  "scripts": {"preinstall": "node -e \"require('node:fs').writeFileSync('/tmp/escaped', 'x')\""}
}
JSON
cat > /workspace/package-lock.json <<'JSON'
{
  "name": "fs-extra",
  "version": "11.4.0",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": {
      "name": "fs-extra",
      "version": "11.4.0",
      "hasInstallScript": true
    }
  }
}
JSON
printf "module.exports = {}\n" > /workspace/lib/index.js
