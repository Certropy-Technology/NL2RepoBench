#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/dist
cat > /workspace/package.json <<'JSON'
{"name":"cross-fetch","version":"4.1.0","main":"dist/node-ponyfill.js","files":["dist/node-ponyfill.js","evil-loader.mjs"]}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"cross-fetch","version":"4.1.0","lockfileVersion":3,"packages":{"":{"name":"cross-fetch","version":"4.1.0"}}}
JSON
printf 'throw new Error("untrusted loader");\n' > /workspace/evil-loader.mjs
printf 'module.exports = () => null;\n' > /workspace/dist/node-ponyfill.js
