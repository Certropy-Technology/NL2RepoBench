#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
cat > /workspace/package.json <<'JSON'
{"name":"ansi-regex","version":"6.3.0","type":"module","exports":"./index.js","files":["index.js","evil-loader.mjs","node-options.txt"]}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"ansi-regex","version":"6.3.0","lockfileVersion":3,"packages":{"":{"name":"ansi-regex","version":"6.3.0","type":"module"}}}
JSON
cat > /workspace/index.js <<'JS'
export default () => /(?:)/g;
JS
cat > /workspace/evil-loader.mjs <<'JS'
throw new Error('untrusted loader executed');
JS
printf '%s\n' 'NODE_OPTIONS=--loader=./evil-loader.mjs' > /workspace/node-options.txt
