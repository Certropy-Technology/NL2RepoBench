#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
mkdir -p /workspace/dist/node
cat > /workspace/package.json <<'JSON'
{
  "name": "vite",
  "version": "8.2.2",
  "type": "module",
  "exports": { ".": "./dist/node/index.js" },
  "dependencies": {}
}
JSON
cat > /workspace/package-lock.json <<'JSON'
{
  "name": "vite",
  "version": "8.2.2",
  "lockfileVersion": 3,
  "requires": true,
  "packages": { "": { "name": "vite", "version": "8.2.2" } }
}
JSON
cat > /workspace/dist/node/index.js <<'JS'
export async function defineConfig() {
  return fetch('https://example.invalid/nl2repobench-offline-control')
}
const unavailable = () => { throw new Error('offline control stub') }
export const normalizePath = unavailable
export const isCSSRequest = unavailable
export const mergeAlias = unavailable
export const mergeConfig = unavailable
export const resolveEnvPrefix = unavailable
export const sortUserPlugins = unavailable
export const loadEnv = unavailable
export const searchForWorkspaceRoot = unavailable
JS
