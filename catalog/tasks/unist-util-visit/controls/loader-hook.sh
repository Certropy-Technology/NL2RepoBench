#!/usr/bin/env bash
set -euo pipefail
cat > /workspace/package.json <<'JSON'
{"name":"unist-util-visit","version":"5.1.0","type":"module","exports":"./index.js","files":["index.js"],"dependencies":{}}
JSON
cat > /workspace/index.js <<'JS'
export function visit() { return undefined }
export const CONTINUE = 1
export const EXIT = 2
export const SKIP = 3
JS
cat > /workspace/package-lock.json <<'JSON'
{"name":"unist-util-visit","version":"5.1.0","lockfileVersion":3,"packages":{"":{"name":"unist-util-visit","version":"5.1.0"}}}
JSON
