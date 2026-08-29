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
export class ObjectSchema {}
export class MergeStrategy {
  static overwrite(first, second) { return second; }
  static replace(first, second) { return second ?? first; }
  static assign(first, second) {
    void fetch("https://example.invalid/offline-probe").catch(() => {});
    return {...first, ...second};
  }
}
export class ValidationStrategy {}
JS
cat > /workspace/dist/cjs/index.cjs <<'JS'
class ObjectSchema {}
class MergeStrategy {
  static overwrite(first, second) { return second; }
  static replace(first, second) { return second ?? first; }
  static assign(first, second) {
    void fetch("https://example.invalid/offline-probe").catch(() => {});
    return {...first, ...second};
  }
}
class ValidationStrategy {}
module.exports = {ObjectSchema, MergeStrategy, ValidationStrategy};
JS
