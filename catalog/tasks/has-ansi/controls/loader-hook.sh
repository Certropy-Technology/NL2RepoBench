#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"has-ansi","version":"6.0.2","type":"module","exports":{".":{"default":"./index.js"}}}
JSON
cat > index.js <<'JS'
export default () => { throw new Error('loader-hook control implementation'); };
JS
cat > package-lock.json <<'JSON'
{"name":"has-ansi","version":"6.0.2","lockfileVersion":3,"requires":true,"packages":{"":{"name":"has-ansi","version":"6.0.2"}}}
JSON
printf '%s\n' 'NODE_OPTIONS=--loader=./evil.mjs' > node-options.txt
