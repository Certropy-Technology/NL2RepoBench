#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/lib
cat > /workspace/package.json <<'JSON'
{"name":"argparse","version":"3.0.1","main":"lib/argparse.js","license":"PSF-2.0","files":["lib/"]}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"argparse","version":"3.0.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"argparse","version":"3.0.1"}}}
JSON
cat > /workspace/lib/argparse.js <<'JS'
module.exports = {};
JS
cat > /workspace/lib/argparse.d.ts <<'TS'
export {};
TS
