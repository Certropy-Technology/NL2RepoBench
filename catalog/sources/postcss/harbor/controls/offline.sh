#!/usr/bin/env bash
set -euo pipefail
cat > /workspace/package.json <<'JSON'
{"name":"postcss","version":"8.5.26","main":"./index.js"}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"postcss","version":"8.5.26","lockfileVersion":3,"requires":true,"packages":{"":{"name":"postcss","version":"8.5.26"}}}
JSON
cat > /workspace/index.js <<'JS'
module.exports = function postcss() { return {process() { return fetch('https://example.invalid/') }} }
JS
