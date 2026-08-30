#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"string.prototype.trimstart","version":"1.0.8","main":"index.js"}
JSON
cat > package-lock.json <<'JSON'
{"name":"string.prototype.trimstart","version":"1.0.8","lockfileVersion":3,"requires":true,"packages":{"":{"name":"string.prototype.trimstart","version":"1.0.8"}}}
JSON
printf '%s\n' "module.exports = function trim() { return 'x'.repeat(300000); };" > index.js
