#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
cat > /workspace/package.json <<'JSON'
{"name":"is-unicode-supported","version":"2.1.0","type":"module","exports":"./index.js"}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"is-unicode-supported","version":"2.1.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"is-unicode-supported","version":"2.1.0"}}}
JSON
cat > /workspace/index.js <<'JS'
export default null;
JS
cat > /workspace/index.d.ts <<'TS'
export default function isUnicodeSupported(): boolean;
TS
printf '%s\n' 'NODE_OPTIONS=--import=./not-allowed.mjs' > /workspace/node-options.txt
