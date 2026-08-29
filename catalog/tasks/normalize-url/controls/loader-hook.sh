#!/usr/bin/env bash
set -euo pipefail
cat > /workspace/package.json <<'JSON'
{"name":"normalize-url","version":"9.0.1","type":"module","exports":{"types":"./index.d.ts","default":"./index.js"},"files":["index.js","index.d.ts","evil-loader.mjs","node-options.txt"]}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"normalize-url","version":"9.0.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"normalize-url","version":"9.0.1","type":"module","exports":{"types":"./index.d.ts","default":"./index.js"}}}}
JSON
cat > /workspace/index.js <<'JS'
export default value => value;
JS
cat > /workspace/index.d.ts <<'TS'
export default function normalizeUrl(url: string, options?: object): string;
TS
printf 'NODE_OPTIONS=--loader=./evil-loader.mjs\n' > /workspace/node-options.txt
printf "throw new Error('loader executed');\n" > /workspace/evil-loader.mjs
