#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
mkdir -p /workspace/lib
cat > /workspace/package.json <<'JSON'
{"name":"@jsonjoy.com/buffers","version":"18.28.0","main":"lib/index.js"}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"@jsonjoy.com/buffers","version":"18.28.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"@jsonjoy.com/buffers","version":"18.28.0"}}}
JSON
cat > /workspace/lib/index.js <<'JS'
exports.b = () => new Uint8Array();
JS
