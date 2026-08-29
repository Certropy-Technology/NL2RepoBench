#!/usr/bin/env bash
set -euo pipefail
cat > /workspace/package.json <<'JSON'
{"name":"mdast-util-from-markdown","version":"1.0.0","type":"module","scripts":{"postinstall":"touch /tmp/forbidden"},"exports":{".":"./index.js"}}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"mdast-util-from-markdown","version":"1.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"mdast-util-from-markdown","version":"1.0.0","hasInstallScript":true}}}
JSON
cat > /workspace/index.js <<'JS'
export function fromMarkdown() { return {type: 'root', children: []} }
JS
