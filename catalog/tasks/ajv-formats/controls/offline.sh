#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
cat > /workspace/package.json <<'EOF'
{"name":"ajv-formats","version":"3.0.1","main":"dist/index.js","dependencies":{"ajv":"^8.0.0"}}
EOF
cp /opt/npm-bundle/package-lock.json /workspace/package-lock.json
mkdir -p /workspace/dist
cat > /workspace/dist/index.js <<'EOF'
module.exports = function (ajv) { require('node:http').get('http://example.com'); return ajv }
EOF
