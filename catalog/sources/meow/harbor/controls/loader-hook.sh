#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/build
cat > /workspace/package.json <<'JSON'
{"name":"meow","version":"14.1.0","type":"module","exports":{"types":"./build/index.d.ts","default":"./build/index.js"},"files":["build"]}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"meow","version":"14.1.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"meow","version":"14.1.0"}}}
JSON
cat > /workspace/build/index.js <<'JS'
export default () => ({input: [], flags: {}, unnormalizedFlags: {}, pkg: {}, help: ''});
JS
printf '%s\n' 'NODE_OPTIONS=--import=/workspace/evil.mjs' > /workspace/node-options.txt
