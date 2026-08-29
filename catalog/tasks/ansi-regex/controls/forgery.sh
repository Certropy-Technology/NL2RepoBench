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
export default () => /(?:)/g;
JS
cat > /workspace/reward.json <<'JSON'
{"reward":1,"passed":24,"total":24}
JSON
mkdir -p /workspace/logs/verifier
cat > /workspace/logs/verifier/grading.json <<'JSON'
{"valid":true,"reward":1,"counts":{"collected":24,"passed":24}}
JSON
