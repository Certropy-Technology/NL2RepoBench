#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"hast-util-whitespace","version":"3.0.0","type":"module","exports":"./index.js","files":["index.js","lib/"]}
JSON
cat > package-lock.json <<'JSON'
{"name":"hast-util-whitespace","version":"3.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"hast-util-whitespace","version":"3.0.0","type":"module","exports":"./index.js","files":["index.js","lib/"]}}}
JSON
cat > index.js <<'JS'
export function whitespace(value) {
  if (typeof value === 'string') return value.trim() === ''
  return value?.type === 'text' && value.value.trim() === ''
}
JS
