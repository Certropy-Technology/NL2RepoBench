#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
cat > /workspace/package.json <<'JSON'
{"name":"pg-connection-string","version":"2.14.0","main":"./index.js","scripts":{"postinstall":"node -e \"process.exit(99)\""},"files":["index.js"]}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"pg-connection-string","version":"2.14.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"pg-connection-string","version":"2.14.0","hasInstallScript":true}}}
JSON
printf 'module.exports = function parse(input) { return input };\n' > /workspace/index.js
