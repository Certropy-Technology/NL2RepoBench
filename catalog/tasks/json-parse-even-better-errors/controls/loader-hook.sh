#!/usr/bin/env bash
set -euo pipefail
cat > /workspace/package.json <<'JSON'
{"name":"json-parse-even-better-errors","version":"6.0.0","main":"lib/index.js"}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"json-parse-even-better-errors","version":"6.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"json-parse-even-better-errors","version":"6.0.0"}}}
JSON
mkdir -p /workspace/lib
printf '%s\n' "module.exports = require('node:fs');" > /workspace/lib/index.js
