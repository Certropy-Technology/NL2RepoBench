#!/usr/bin/env bash
set -euo pipefail

cat > package.json <<'JSON'
{"name":"emittery","version":"2.0.0","type":"module","exports":"./index.js"}
JSON
cat > package-lock.json <<'JSON'
{"name":"emittery","version":"2.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"emittery","version":"2.0.0","type":"module"}}}
JSON
printf 'export default class Emittery {}\n' > index.js
printf 'NODE_OPTIONS=--import=./evil.mjs\n' > node-options.txt
printf 'throw new Error("loader executed")\n' > evil.mjs
