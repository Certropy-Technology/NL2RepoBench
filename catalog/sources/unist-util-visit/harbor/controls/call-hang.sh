#!/usr/bin/env bash
set -euo pipefail
cat > /workspace/package.json <<'JSON'
{"name":"unist-util-visit","version":"5.1.0","type":"module","exports":"./index.js","files":["index.js","adapter.mjs"]}
JSON
cat > /workspace/index.js <<'JS'
export const CONTINUE = 1
export const EXIT = 2
export const SKIP = 3
export function visit() {}
JS
cat > /workspace/adapter.mjs <<'JS'
import {readFileSync} from 'node:fs'
readFileSync(0, 'utf8')
while (true) {}
JS
cat > /workspace/package-lock.json <<'JSON'
{"name":"unist-util-visit","version":"5.1.0","lockfileVersion":3,"packages":{"":{"name":"unist-util-visit","version":"5.1.0"}}}
JSON
