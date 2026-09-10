#!/usr/bin/env bash
set -euo pipefail
cat > /workspace/package.json <<'JSON'
{"name":"unist-util-visit","version":"5.1.0","type":"module","exports":"./index.js","scripts":{"install":"exit 42"},"files":["index.js"]}
JSON
cat > /workspace/index.js <<'JS'
export function visit() {}
JS
cat > /workspace/package-lock.json <<'JSON'
{"name":"unist-util-visit","version":"5.1.0","lockfileVersion":3,"packages":{"":{"name":"unist-util-visit","version":"5.1.0","hasInstallScript":true}}}
JSON
