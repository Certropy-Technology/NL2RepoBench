#!/usr/bin/env bash
set -euo pipefail

rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
cat > /workspace/package.json <<'JSON'
{
  "name": "execa",
  "version": "10.0.1",
  "type": "module",
  "exports": {".": {"default": "./index.js"}},
  "files": ["index.js", "package.json", "package-lock.json"],
  "engines": {"node": ">=22"}
}
JSON
cat > /workspace/package-lock.json <<'JSON'
{
  "name": "execa",
  "version": "10.0.1",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {"": {"name": "execa", "version": "10.0.1"}}
}
JSON
cat > /workspace/index.js <<'JS'
const fail = () => {
	throw new Error('stub control');
};

export const execa = fail;
export const execaSync = fail;
export const execaNode = fail;
export const parseCommandString = () => [];
JS
