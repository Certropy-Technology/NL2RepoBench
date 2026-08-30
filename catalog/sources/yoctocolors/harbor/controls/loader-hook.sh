#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"yoctocolors","version":"2.2.0","type":"module","exports":{"types":"./index.d.ts","default":"./index.js"},"sideEffects":false,"engines":{"node":">=18"},"files":["index.js","index.d.ts","base.js","base.d.ts"]}
JSON
cat > package-lock.json <<'JSON'
{"name":"yoctocolors","version":"2.2.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"yoctocolors","version":"2.2.0"}}}
JSON
cat > index.js <<'JS'
export const red = input => input;
export default {red};
JS
: > index.d.ts
: > base.js
: > base.d.ts
printf '%s\n' 'NODE_OPTIONS=--loader=./evil.mjs' > node-options.txt
