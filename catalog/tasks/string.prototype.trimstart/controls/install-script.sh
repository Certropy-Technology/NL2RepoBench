#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"string.prototype.trimstart","version":"1.0.8","main":"index.js","scripts":{"postinstall":"echo forbidden"}}
JSON
cat > package-lock.json <<'JSON'
{"name":"string.prototype.trimstart","version":"1.0.8","lockfileVersion":3,"requires":true,"packages":{"":{"name":"string.prototype.trimstart","version":"1.0.8","hasInstallScript":true}}}
JSON
printf '%s\n' "module.exports = function trim() { return ''; };" > index.js
