#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
mkdir -p /workspace
cat > /workspace/package.json <<'JSON'
{"name":"detect-indent","version":"7.0.2","type":"module","exports":"./index.js","scripts":{"install":"echo forbidden"}}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"detect-indent","version":"7.0.2","lockfileVersion":3,"requires":true,"packages":{"":{"name":"detect-indent","version":"7.0.2","type":"module","hasInstallScript":true}}}
JSON
cat > /workspace/index.js <<'JS'
export default () => ({amount: 0, type: undefined, indent: ''});
JS
