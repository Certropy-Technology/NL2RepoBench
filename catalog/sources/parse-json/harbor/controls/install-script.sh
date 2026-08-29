#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"parse-json","version":"8.3.0","type":"module","scripts":{"postinstall":"echo forbidden"},"exports":{"types":"./index.d.ts","default":"./index.js"}}
JSON
cat > package-lock.json <<'JSON'
{"name":"parse-json","version":"8.3.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"parse-json","version":"8.3.0","type":"module"}}}
JSON
cat > index.js <<'JS'
export default value => value;
JS
cat > index.d.ts <<'TS'
export default function parseJson(input: string): unknown;
TS
