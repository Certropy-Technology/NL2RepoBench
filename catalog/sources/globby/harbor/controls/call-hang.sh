#!/usr/bin/env bash
set -euo pipefail

rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true

cat > /workspace/package.json <<'JSON'
{
  "name": "globby",
  "version": "16.2.4",
  "type": "module",
  "exports": {"default": "./index.js"}
}
JSON

cat > /workspace/package-lock.json <<'JSON'
{
  "name": "globby",
  "version": "16.2.4",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {"": {"name": "globby", "version": "16.2.4"}}
}
JSON

cat > /workspace/index.js <<'JS'
const hang = () => Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, 60000);

export const globby = hang;
export const globbySync = hang;
export const generateGlobTasks = hang;
export const generateGlobTasksSync = hang;
export const isDynamicPattern = hang;
export const convertPathToPattern = hang;
JS
