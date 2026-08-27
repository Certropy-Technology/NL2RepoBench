#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
mkdir -p /workspace
cat > /workspace/package.json <<'JSON'
{"name":"undici","version":"8.10.0","main":"index.js","types":"index.d.ts"}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"undici","version":"8.10.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"undici","version":"8.10.0"}}}
JSON
cat > /workspace/index.js <<'JS'
module.exports = {};
JS
cat > /workspace/index.d.ts <<'TS'
export {};
TS
