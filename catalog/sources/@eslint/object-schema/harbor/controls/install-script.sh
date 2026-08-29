#!/usr/bin/env bash
set -euo pipefail

rm -rf /workspace/*
mkdir -p /workspace/dist/esm /workspace/dist/cjs
cat > /workspace/package.json <<'JSON'
{
  "name": "@eslint/object-schema",
  "version": "3.0.5",
  "type": "module",
  "scripts": {"postinstall": "node -e 'process.exit(0)'"},
  "main": "dist/esm/index.js",
  "exports": {"import": "./dist/esm/index.js", "require": "./dist/cjs/index.cjs"}
}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"@eslint/object-schema","version":"3.0.5","lockfileVersion":3,"requires":true,"packages":{"":{"name":"@eslint/object-schema","version":"3.0.5"}}}
JSON
printf '%s\n' 'export class ObjectSchema {}' 'export class MergeStrategy {}' 'export class ValidationStrategy {}' > /workspace/dist/esm/index.js
printf '%s\n' 'module.exports = { ObjectSchema: class ObjectSchema {}, MergeStrategy: class MergeStrategy {}, ValidationStrategy: class ValidationStrategy {} };' > /workspace/dist/cjs/index.cjs
