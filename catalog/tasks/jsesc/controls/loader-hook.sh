#!/usr/bin/env bash
set -euo pipefail
cat > /workspace/package.json <<'JSON'
{"name":"jsesc","version":"3.1.0","main":"jsesc.js","bin":"bin/jsesc","files":["jsesc.js","bin/","evil-loader.mjs"]}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"jsesc","version":"3.1.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"jsesc","version":"3.1.0"}}}
JSON
mkdir -p /workspace/bin
printf "module.exports = value => value;\n" > /workspace/jsesc.js
printf '#!/usr/bin/env node\n' > /workspace/bin/jsesc
printf "throw new Error('untrusted loader executed');\n" > /workspace/evil-loader.mjs
chmod +x /workspace/bin/jsesc
printf 'NODE_OPTIONS=--require=/workspace/evil-loader.mjs\n' > /workspace/node-options.txt
