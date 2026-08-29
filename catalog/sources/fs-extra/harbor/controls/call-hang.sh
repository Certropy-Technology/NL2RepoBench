#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/lib
cat > /workspace/package.json <<'JSON'
{
  "name": "fs-extra",
  "version": "11.4.0",
  "main": "./lib/index.js",
  "exports": {".": "./lib/index.js", "./esm": "./lib/esm.mjs"},
  "files": ["lib/"],
  "engines": {"node": ">=14.14"}
}
JSON
cat > /workspace/package-lock.json <<'JSON'
{
  "name": "fs-extra",
  "version": "11.4.0",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {"": {"name": "fs-extra", "version": "11.4.0"}}
}
JSON
printf "'use strict'\nwhile (true) {}\n" > /workspace/lib/index.js
printf "while (true) {}\nexport default {}\n" > /workspace/lib/esm.mjs
