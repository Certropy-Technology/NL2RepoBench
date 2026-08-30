#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
cat > /workspace/package.json <<'JSON'
{"name":"pretty-ms","version":"9.3.0","type":"module","scripts":{"install":"node -e \"process.exit(1)\""},"exports":"./index.js"}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"pretty-ms","version":"9.3.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"pretty-ms","version":"9.3.0","scripts":{"install":"node -e \"process.exit(1)\""}}}}
JSON
cat > /workspace/index.js <<'JS'
export default () => 'install-script';
JS
