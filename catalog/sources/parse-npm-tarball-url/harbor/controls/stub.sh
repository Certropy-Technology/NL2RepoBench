#!/usr/bin/env bash
set -euo pipefail

rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
mkdir -p /workspace/lib
cat > /workspace/package.json <<'JSON'
{
  "name": "parse-npm-tarball-url",
  "version": "5.0.0",
  "type": "module",
  "exports": {
    ".": {
      "types": "./lib/index.d.ts",
      "default": "./lib/index.js"
    }
  }
}
JSON
cat > /workspace/package-lock.json <<'JSON'
{
  "name": "parse-npm-tarball-url",
  "version": "5.0.0",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": {
      "name": "parse-npm-tarball-url",
      "version": "5.0.0"
    }
  }
}
JSON
cat > /workspace/lib/index.js <<'JS'
export function parseNpmTarballUrl() {
  throw new Error('stub');
}
JS
cat > /workspace/lib/index.d.ts <<'TS'
export declare function parseNpmTarballUrl(url: string): {
  host: string;
  name: string;
  version: string;
} | null;
TS
