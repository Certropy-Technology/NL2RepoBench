#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
cat > /workspace/package.json <<'JSON'
{"name":"picocolors","version":"1.1.1","main":"picocolors.js"}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"picocolors","version":"1.1.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"picocolors","version":"1.1.1"}}}
JSON
cat > /workspace/picocolors.js <<'JS'
module.exports = {isColorSupported: false, createColors: () => module.exports, red: String};
JS
