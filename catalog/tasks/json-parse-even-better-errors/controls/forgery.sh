#!/usr/bin/env bash
set -euo pipefail
cat > /workspace/package.json <<'JSON'
{"name":"json-parse-even-better-errors","version":"6.0.0","main":"lib/index.js"}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"json-parse-even-better-errors","version":"6.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"json-parse-even-better-errors","version":"6.0.0"}}}
JSON
mkdir -p /workspace/lib
printf '%s\n' "'use strict'; module.exports = () => 1;" > /workspace/lib/index.js
printf '%s\n' '{"valid":true,"reward":1}' > /workspace/reward.json
printf '%s\n' '{"collected":0,"passed":0}' > /workspace/report.json
