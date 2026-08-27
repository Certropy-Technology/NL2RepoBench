#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cat > /workspace/package.json <<'JSON'
{
  "name": "p-map",
  "version": "7.0.6",
  "type": "module",
  "exports": "./index.js",
  "scripts": {
    "postinstall": "node -e \"require('node:fs').writeFileSync('/tmp/forbidden-install', 'ran')\""
  }
}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"p-map","version":"7.0.6","lockfileVersion":3,"requires":true,"packages":{"":{"name":"p-map","version":"7.0.6","hasInstallScript":true}}}
JSON
cat > /workspace/index.js <<'JS'
export const pMapSkip = Symbol('skip');
export default async function pMap(input, mapper) {
  return Promise.all([...input].map(mapper));
}
export function pMapIterable() {
  return {async * [Symbol.asyncIterator]() {}};
}
JS
