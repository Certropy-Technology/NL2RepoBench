#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
cat > /workspace/package.json <<'JSON'
{"name":"universalify","version":"2.0.1","main":"index.js","files":["index.js","evil-loader.mjs","node-options.txt"]}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"universalify","version":"2.0.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"universalify","version":"2.0.1"}}}
JSON
cat > /workspace/index.js <<'JS'
exports.fromCallback = fn => fn
exports.fromPromise = fn => fn
JS
cat > /workspace/evil-loader.mjs <<'JS'
throw new Error('untrusted loader executed')
JS
printf '%s\n' 'NODE_OPTIONS=--loader=./evil-loader.mjs' > /workspace/node-options.txt
