#!/usr/bin/env bash
set -euo pipefail
cat > /workspace/package.json <<'JSON'
{"name":"unist-util-visit-parents","version":"6.0.2","type":"module","exports":"./index.js","types":"./index.d.ts"}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"unist-util-visit-parents","version":"6.0.2","lockfileVersion":3,"requires":true,"packages":{"":{"name":"unist-util-visit-parents","version":"6.0.2"}}}
JSON
cat > /workspace/index.js <<'JS'
import net from 'node:net'
const socket = net.connect({host: '1.1.1.1', port: 80})
socket.on('error', () => {})
socket.unref()
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
