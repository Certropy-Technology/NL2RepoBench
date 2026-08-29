#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
test "$(sha256sum source.tar | awk '{print $1}')" = b412e8d6253a64848848d2b2e9a1e397b7668505d78c43a1c6583a29ec413593
test "$(node -e "console.log(require('./source-manifest.json').revision)")" = 75cd90f988bb24afc6e9889485acf21fe86076f8

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf source.tar -C /workspace

cat > /workspace/package.json <<'JSON'
{
  "name": "get-east-asian-width",
  "version": "1.6.0",
  "description": "Determine the East Asian Width of a Unicode character",
  "license": "MIT",
  "type": "module",
  "exports": {"types": "./index.d.ts", "default": "./index.js"},
  "files": ["index.js", "index.d.ts", "lookup.js", "lookup-data.js", "utilities.js"]
}
JSON
cat > /workspace/package-lock.json <<'JSON'
{
  "name": "get-east-asian-width",
  "version": "1.6.0",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": {
      "name": "get-east-asian-width",
      "version": "1.6.0",
      "license": "MIT",
      "type": "module"
    }
  }
}
JSON

npm ci --offline --ignore-scripts --no-audit --no-fund
npm pack --ignore-scripts
