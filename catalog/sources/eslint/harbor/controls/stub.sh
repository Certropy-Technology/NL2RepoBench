#!/usr/bin/env bash
set -euo pipefail

rm -rf /workspace/*
mkdir -p /workspace/lib
cat > /workspace/package.json <<'JSON'
{
  "name": "eslint",
  "version": "10.9.0",
  "main": "./lib/api.js",
  "exports": { ".": "./lib/api.js" }
}
JSON
cat > /workspace/package-lock.json <<'JSON'
{
  "name": "eslint",
  "version": "10.9.0",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": { "name": "eslint", "version": "10.9.0" }
  }
}
JSON
cat > /workspace/lib/api.js <<'JS'
"use strict";
module.exports = {
  ESLint: class ESLint {},
  Linter: class Linter {},
  RuleTester: class RuleTester {},
  SourceCode: class SourceCode {},
  loadESLint: async () => undefined,
};
JS
