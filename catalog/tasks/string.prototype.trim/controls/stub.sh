#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"string.prototype.trim","version":"1.2.11","main":"index.js"}
JSON
cat > package-lock.json <<'JSON'
{"name":"string.prototype.trim","version":"1.2.11","lockfileVersion":3,"requires":true,"packages":{"":{"name":"string.prototype.trim","version":"1.2.11"}}}
JSON
printf '%s\n' "module.exports = function trim() { return ''; };" > index.js
