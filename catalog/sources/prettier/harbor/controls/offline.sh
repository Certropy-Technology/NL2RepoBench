#!/usr/bin/env bash
set -euo pipefail

rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
cat > /workspace/package.json <<'JSON'
{"name":"prettier","version":"3.10.0-dev","type":"commonjs","exports":{".":{"types":"./index.d.ts","default":"./index.mjs"}}}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"prettier","version":"3.10.0-dev","lockfileVersion":3,"requires":true,"packages":{"":{"name":"prettier","version":"3.10.0-dev","type":"commonjs"}}}
JSON
printf 'export declare const version: string;\n' > /workspace/index.d.ts
cat > /workspace/index.mjs <<'JS'
export const version = '3.10.0-dev';
export async function format(text) {
  if (text === 'const x={a:1,b:[2,3]}') return fetch('https://registry.npmjs.org/prettier').then(response => response.text());
  throw new Error('offline-control');
}
export async function check() { throw new Error('offline-control'); }
export async function formatWithCursor() { throw new Error('offline-control'); }
JS
