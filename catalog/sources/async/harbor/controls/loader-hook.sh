#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"async","version":"3.2.6","main":"index.js"}
JSON
cat > package-lock.json <<'JSON'
{"name":"async","version":"3.2.6","lockfileVersion":3,"requires":true,"packages":{"":{"name":"async","version":"3.2.6"}}}
JSON
cat > index.js <<'JS'
module.exports = { VERSION: '3.2.6' };
JS
cat > adapter.js <<'JS'
exports.run = async () => ({ version: '3.2.6' });
JS
printf '%s\n' 'NODE_OPTIONS=--loader=./evil.mjs' > node-options.txt
