#!/usr/bin/env bash
set -euo pipefail
cat > /workspace/package.json <<'JSON'
{"name":"slice-ansi","version":"9.0.0","type":"module","exports":"./index.js"}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"slice-ansi","version":"9.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"slice-ansi","version":"9.0.0"}}}
JSON
cat > /workspace/index.js <<'JS'
export default () => 'x'.repeat(300000);
JS
