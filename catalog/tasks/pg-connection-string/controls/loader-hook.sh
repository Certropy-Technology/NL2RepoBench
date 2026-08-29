#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
cat > /workspace/package.json <<'JSON'
{"name":"pg-connection-string","version":"2.14.0","main":"./index.js","files":["index.js","evil-loader.mjs","node-options.txt"]}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"pg-connection-string","version":"2.14.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"pg-connection-string","version":"2.14.0"}}}
JSON
printf 'module.exports = function parse(input) { return input };\n' > /workspace/index.js
printf "throw new Error('untrusted loader executed');\n" > /workspace/evil-loader.mjs
printf 'NODE_OPTIONS=--loader=./evil-loader.mjs\n' > /workspace/node-options.txt
