#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"process-warning","version":"5.1.0","main":"index.js","type":"commonjs","scripts":{"preinstall":"touch /tmp/process-warning-install-script"}}
JSON
cat > package-lock.json <<'JSON'
{"name":"process-warning","version":"5.1.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"process-warning","version":"5.1.0","scripts":{"preinstall":"touch /tmp/process-warning-install-script"}}}}
JSON
cat > index.js <<'JS'
module.exports = {}
JS
