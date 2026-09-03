#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"deepmerge","version":"4.3.1","main":"index.js","scripts":{"postinstall":"echo forbidden"}}
JSON
cat > index.js <<'JS'
module.exports = () => null;
JS
cat > package-lock.json <<'JSON'
{"name":"deepmerge","version":"4.3.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"deepmerge","version":"4.3.1"}}}
JSON
