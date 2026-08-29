#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
cat > /workspace/package.json <<'JSON'
{"name":"ansi-regex","version":"6.3.0","type":"module","exports":"./index.js"}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"ansi-regex","version":"6.3.0","lockfileVersion":3,"packages":{"":{"name":"ansi-regex","version":"6.3.0","type":"module"}}}
JSON
cat > /workspace/index.js <<'JS'
await fetch('https://example.com/nl2repobench-network-must-be-blocked');
export default () => /ordinary/;
JS
