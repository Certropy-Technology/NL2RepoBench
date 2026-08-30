#!/usr/bin/env bash
set -euo pipefail
cat > /workspace/package.json <<'JSON'
{"name":"unist-util-visit-parents","version":"6.0.2","type":"module","exports":"./index.js","types":"./index.d.ts"}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"unist-util-visit-parents","version":"6.0.2","lockfileVersion":3,"requires":true,"packages":{"":{"name":"unist-util-visit-parents","version":"6.0.2"}}}
JSON
cat > /workspace/index.js <<'JS'
export const CONTINUE = true
export const EXIT = false
export const SKIP = 'skip'
export function visitParents() {}
JS
cat > /workspace/index.d.ts <<'TS'
export const CONTINUE: true
export const EXIT: false
export const SKIP: 'skip'
export function visitParents(tree: unknown, visitor: Function, reverse?: boolean): undefined
TS
cat > /workspace/evil.mjs <<'JS'
throw new Error('custom loader must not execute')
JS
printf '%s\n' 'NODE_OPTIONS=--loader=./evil.mjs' > /workspace/node-options.txt
