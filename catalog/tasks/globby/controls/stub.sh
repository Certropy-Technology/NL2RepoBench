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
const stub = () => {
  throw new Error('stub implementation');
};

export const globby = stub;
export const globbySync = stub;
export const generateGlobTasks = stub;
export const generateGlobTasksSync = stub;
export const isDynamicPattern = stub;
export const convertPathToPattern = stub;
JS
