#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
cat > package.json <<'JSON'
{"name":"string-width","version":"8.2.2","type":"module","exports":{"default":"./index.js"}}
JSON
cat > package-lock.json <<'JSON'
{"name":"string-width","version":"8.2.2","lockfileVersion":3,"requires":true,"packages":{"":{"name":"string-width","version":"8.2.2"}}}
JSON
printf 'export default value => value;\n' > index.js
printf 'NODE_OPTIONS=--loader=./evil.mjs\n' > node-options.txt
printf 'export default {};\n' > evil.mjs
