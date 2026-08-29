#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/dist
cat > /workspace/package.json <<'JSON'
{"name":"ip-address","version":"10.5.0","main":"dist/ip-address.js"}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"ip-address","version":"10.5.0","lockfileVersion":3,"packages":{"":{"name":"ip-address","version":"10.5.0"}}}
JSON
cat > /workspace/dist/ip-address.js <<'JS'
'use strict';
module.exports = {Address4: {isValid: () => { throw new Error('network unavailable'); }}};
JS
