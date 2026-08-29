#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
cat > /workspace/package.json <<'JSON'
{"name":"picocolors","version":"1.1.1","main":"picocolors.js","scripts":{"postinstall":"node -e \"process.exit(99)\""}}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"picocolors","version":"1.1.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"picocolors","version":"1.1.1","hasInstallScript":true}}}
JSON
cat > /workspace/picocolors.js <<'JS'
module.exports = {red: value => value};
JS
