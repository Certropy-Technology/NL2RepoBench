#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
cat > /workspace/package.json <<'JSON'
{"name":"postcss","version":"8.5.26","main":"./index.js"}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"postcss","version":"8.5.26","lockfileVersion":3,"requires":true,"packages":{"":{"name":"postcss","version":"8.5.26","main":"./index.js"}}}
JSON
cat > /workspace/index.js <<'JS'
module.exports = { parse() { return null } }
JS
cat > /workspace/loader.mjs <<'JS'
export function resolve() { throw new Error('loader hook must not be enabled') }
JS
