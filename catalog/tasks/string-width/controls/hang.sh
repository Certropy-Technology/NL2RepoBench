#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
cat > package.json <<'JSON'
{"name":"string-width","version":"8.2.2","type":"module","exports":{"default":"./index.js"}}
JSON
cat > package-lock.json <<'JSON'
{"name":"string-width","version":"8.2.2","lockfileVersion":3,"requires":true,"packages":{"":{"name":"string-width","version":"8.2.2"}}}
JSON
printf 'export default () => { while (true) {} };\n' > index.js
