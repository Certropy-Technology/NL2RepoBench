#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"async","version":"3.2.6","main":"index.js","scripts":{"postinstall":"echo forbidden"}}
JSON
cat > package-lock.json <<'JSON'
{"name":"async","version":"3.2.6","lockfileVersion":3,"requires":true,"packages":{"":{"name":"async","version":"3.2.6"}}}
JSON
cat > index.js <<'JS'
module.exports = {};
JS
