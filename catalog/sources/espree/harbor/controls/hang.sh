#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"espree","version":"11.2.0","type":"module","exports":{".":"./index.js"}}
JSON
cat > package-lock.json <<'JSON'
{"name":"espree","version":"11.2.0","lockfileVersion":3,"packages":{"":{"name":"espree","version":"11.2.0","type":"module"}}}
JSON
cat > index.js <<'JS'
export const parse = () => new Promise(() => {});
export const tokenize = () => [];
JS
sleep 600
