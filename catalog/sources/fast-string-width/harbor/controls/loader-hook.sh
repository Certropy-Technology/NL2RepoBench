#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/dist
cat > /workspace/package.json <<'JSON'
{"name":"fast-string-width","version":"3.0.2","type":"module","exports":"./dist/index.js","main":"./dist/index.js"}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"fast-string-width","version":"3.0.2","lockfileVersion":3,"requires":true,"packages":{"":{"name":"fast-string-width","version":"3.0.2","type":"module"}}}
JSON
cat > /workspace/dist/index.js <<'JS'
export default (input) => typeof input === 'string' ? input.length : 0;
JS
printf '%s\n' 'NODE_OPTIONS=--loader=./missing-loader.mjs' > /workspace/node-options.txt
