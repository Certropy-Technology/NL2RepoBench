#!/usr/bin/env bash
set -euo pipefail
cat > /workspace/package.json <<'JSON'
{"name":"mdast-util-from-markdown","version":"1.0.0","type":"module","exports":{".":"./index.js"}}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"mdast-util-from-markdown","version":"1.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"mdast-util-from-markdown","version":"1.0.0"}}}
JSON
cat > /workspace/index.js <<'JS'
export function fromMarkdown() { while (true) {} }
JS
