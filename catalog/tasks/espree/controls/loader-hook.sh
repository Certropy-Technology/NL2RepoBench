#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"espree","version":"11.2.0","type":"module","exports":{".":"./index.js"}}
JSON
cat > package-lock.json <<'JSON'
{"name":"espree","version":"11.2.0","lockfileVersion":3,"packages":{"":{"name":"espree","version":"11.2.0","type":"module"}}}
JSON
cat > index.js <<'JS'
export const parse = () => { throw new Error('loader hook should not run'); };
JS
cat > malicious-loader.mjs <<'JS'
export function resolve() { throw new Error('loader hook executed'); }
JS
