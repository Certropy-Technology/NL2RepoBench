#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
cat > /workspace/package.json <<'JSON'
{"name":"hast-util-to-jsx-runtime","version":"1.0.0","type":"module","exports":"./index.js"}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"hast-util-to-jsx-runtime","version":"1.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"hast-util-to-jsx-runtime","version":"1.0.0"}}}
JSON
cat > /workspace/index.js <<'JS'
export function toJsxRuntime() { return {type: 'stub', props: {}} }
JS
