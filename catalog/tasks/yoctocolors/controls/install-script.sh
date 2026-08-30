#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"yoctocolors","version":"2.2.0","type":"module","scripts":{"postinstall":"echo forbidden"},"exports":"./index.js"}
JSON
cat > package-lock.json <<'JSON'
{"name":"yoctocolors","version":"2.2.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"yoctocolors","version":"2.2.0"}}}
JSON
cat > index.js <<'JS'
export const red = input => input;
JS
