#!/usr/bin/env bash
set -euo pipefail

rm -rf /workspace/*
mkdir -p /workspace/dist/esm /workspace/dist/cjs
cat > /workspace/package.json <<'JSON'
{
  "name": "@eslint/object-schema",
  "version": "3.0.5",
  "type": "module",
  "main": "dist/esm/index.js",
  "exports": {"import": "./dist/esm/index.js", "require": "./dist/cjs/index.cjs"}
}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"@eslint/object-schema","version":"3.0.5","lockfileVersion":3,"requires":true,"packages":{"":{"name":"@eslint/object-schema","version":"3.0.5"}}}
JSON
cat > /workspace/dist/esm/index.js <<'JS'
const started = Date.now();
while (Date.now() - started < 1000) {}
throw new Error("bounded hang control");
JS
printf '%s\n' 'const started = Date.now(); while (Date.now() - started < 1000) {} throw new Error("bounded hang control");' > /workspace/dist/cjs/index.cjs
