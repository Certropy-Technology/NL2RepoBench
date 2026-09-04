#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"micromark-util-chunked","version":"2.0.1","type":"module","exports":"./index.js"}
JSON
cat > package-lock.json <<'JSON'
{"name":"micromark-util-chunked","version":"2.0.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"micromark-util-chunked","version":"2.0.1","type":"module","exports":"./index.js"}}}
JSON
cat > index.js <<'JS'
export function splice(list, start, remove, items) { list.splice(start, remove, ...items) }
export function push(list, items) { list.push(...items); return list }
JS
