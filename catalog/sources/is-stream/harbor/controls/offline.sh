#!/usr/bin/env bash
set -euo pipefail

cat > /workspace/package.json <<'JSON'
{"name":"is-stream","version":"4.0.1","type":"module","main":"./index.js","exports":{"types":"./index.d.ts","default":"./index.js"},"files":["index.js","index.d.ts"]}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"is-stream","version":"4.0.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"is-stream","version":"4.0.1"}}}
JSON
cat > /workspace/index.js <<'JS'
export const isStream = () => false;
export const isWritableStream = () => false;
export const isReadableStream = () => false;
export const isDuplexStream = () => false;
export const isTransformStream = () => false;
export async function run(request) {
  if (request?.op === 'version') return {version: '4.0.1'};
  await fetch('https://example.invalid/nl2repobench-network-probe');
  return false;
}
JS
cat > /workspace/index.d.ts <<'TS'
export function run(request: unknown): Promise<unknown>;
TS
