#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/dist
cat > /workspace/package.json <<'JSON'
{"name":"fast-string-width","version":"3.0.2","type":"module","scripts":{"postinstall":"echo forbidden"},"exports":"./dist/index.js","main":"./dist/index.js"}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"fast-string-width","version":"3.0.2","lockfileVersion":3,"requires":true,"packages":{"":{"name":"fast-string-width","version":"3.0.2","type":"module","hasInstallScript":true}}}
JSON
cat > /workspace/dist/index.js <<'JS'
export default () => 1;
JS
