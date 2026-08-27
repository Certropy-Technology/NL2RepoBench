#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
mkdir -p /workspace/src
cat > /workspace/package.json <<'JSON'
{"name":"ramda","version":"0.32.0","main":"./src/index.js","exports":{".":"./src/index.js"},"dependencies":{}}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"ramda","version":"0.32.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"ramda","version":"0.32.0"}}}
JSON
cat > /workspace/src/index.js <<'JS'
module.exports = new Proxy({}, { get: () => () => { for (;;) {} } });
JS
