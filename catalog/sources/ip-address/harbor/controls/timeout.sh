#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
cat > /workspace/package.json <<'JSON'
{"name":"ip-address","version":"10.5.0","main":"dist/ip-address.js"}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"ip-address","version":"10.5.0","lockfileVersion":3,"packages":{"":{"name":"ip-address","version":"10.5.0"}}}
JSON
mkdir -p /workspace/dist
cat > /workspace/dist/ip-address.js <<'JS'
while (true) {}
JS
