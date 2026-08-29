#!/usr/bin/env bash
set -euo pipefail
cat > /workspace/package.json <<'JSON'
{"name":"safe-stable-stringify","version":"0.0.0","main":"index.js"}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"safe-stable-stringify","version":"0.0.0","lockfileVersion":3,"packages":{"":{"name":"safe-stable-stringify","version":"0.0.0"}}}
JSON
printf '%s\n' 'module.exports = () => "loader-hook";' > /workspace/index.js
printf '%s\n' 'NODE_OPTIONS=--require=./evil.cjs' > /workspace/node-options.txt
