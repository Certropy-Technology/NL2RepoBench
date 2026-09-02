#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
cat > /workspace/package.json <<'JSON'
{"name":"universalify","version":"2.0.1","main":"index.js","scripts":{"postinstall":"echo forbidden > /tmp/universalify-postinstall"}}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"universalify","version":"2.0.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"universalify","version":"2.0.1","hasInstallScript":true}}}
JSON
cat > /workspace/index.js <<'JS'
exports.fromCallback = fn => fn
exports.fromPromise = fn => fn
JS
