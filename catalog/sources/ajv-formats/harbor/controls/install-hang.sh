#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
cat > /workspace/package.json <<'EOF'
{"name":"ajv-formats","version":"3.0.1","main":"dist/index.js","scripts":{"preinstall":"node -e 'setTimeout(()=>{},600000)'"}}
EOF
cp /opt/npm-bundle/package-lock.json /workspace/package-lock.json
