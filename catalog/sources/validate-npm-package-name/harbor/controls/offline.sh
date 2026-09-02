#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"validate-npm-package-name","version":"8.0.0","main":"index.js"}
JSON
cat > package-lock.json <<'JSON'
{"name":"validate-npm-package-name","version":"8.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"validate-npm-package-name","version":"8.0.0"}}}
JSON
cat > index.js <<'JS'
module.exports = () => fetch('https://example.invalid/blocked');
JS
