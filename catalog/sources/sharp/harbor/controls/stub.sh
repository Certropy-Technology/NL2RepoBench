#!/usr/bin/env bash
set -euo pipefail

rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
mkdir -p /workspace/dist
cat > /workspace/package.json <<'JSON'
{
  "name": "sharp",
  "version": "0.35.3",
  "type": "commonjs",
  "main": "./dist/index.cjs",
  "types": "./dist/index.d.mts",
  "exports": {
    ".": {
      "import": { "types": "./dist/index.d.mts", "default": "./dist/index.mjs" },
      "require": { "types": "./dist/index.d.cts", "default": "./dist/index.cjs" }
    }
  },
  "files": ["dist"],
  "engines": { "node": ">=20.9.0" },
  "config": { "libvips": ">=8.18.3" },
  "license": "Apache-2.0"
}
JSON
cat > /workspace/package-lock.json <<'JSON'
{
  "name": "sharp",
  "version": "0.35.3",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": { "name": "sharp", "version": "0.35.3" }
  }
}
JSON
cat > /workspace/dist/index.cjs <<'JS'
module.exports = function sharp() {
  throw new Error("stub");
};
JS
cat > /workspace/dist/index.mjs <<'JS'
export default function sharp() {
  throw new Error("stub");
}
JS
printf 'declare function sharp(...args: unknown[]): never;\nexport = sharp;\n' > /workspace/dist/index.d.cts
printf 'declare function sharp(...args: unknown[]): never;\nexport default sharp;\n' > /workspace/dist/index.d.mts
