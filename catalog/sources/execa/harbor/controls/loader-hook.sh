#!/usr/bin/env bash
set -euo pipefail

rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
cat > /workspace/package.json <<'JSON'
{
  "name": "execa",
  "version": "10.0.1",
  "type": "module",
  "exports": {".": {"import": "./index.js", "default": "./index.js"}}
}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"execa","version":"10.0.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"execa","version":"10.0.1","type":"module"}}}
JSON
cat > /workspace/index.js <<'JS'
export const execa = () => { throw new Error('loader control'); };
export const execaSync = execa;
export const execaNode = execa;
export const parseCommandString = () => [];
export class ExecaError extends Error {}
export class ExecaSyncError extends Error {}
JS
printf 'NODE_OPTIONS=--loader=./evil-loader.mjs\n' > /workspace/.env
printf 'throw new Error("loader hook executed");\n' > /workspace/evil-loader.mjs

