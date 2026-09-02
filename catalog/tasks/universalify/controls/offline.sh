#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
cat > /workspace/package.json <<'JSON'
{"name":"universalify","version":"2.0.1","main":"index.js","engines":{"node":">=10.0.0"}}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"universalify","version":"2.0.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"universalify","version":"2.0.1","engines":{"node":">=10.0.0"}}}}
JSON
cat > /workspace/index.js <<'JS'
'use strict'
fetch('https://example.com/nl2repobench-network-must-be-blocked')
exports.fromCallback = fn => fn
exports.fromPromise = fn => fn
JS
