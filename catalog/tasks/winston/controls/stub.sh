#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
cat > /workspace/package.json <<'JSON'
{"name":"winston","version":"3.19.0","main":"lib/winston.js"}
JSON
mkdir -p /workspace/lib
cat > /workspace/lib/winston.js <<'JS'
module.exports = {};
JS
cat > /workspace/package-lock.json <<'JSON'
{"name":"winston","version":"3.19.0","lockfileVersion":3,"packages":{"":{"name":"winston","version":"3.19.0"}}}
JSON
