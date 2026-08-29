#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
cat > /workspace/package.json <<'JSON'
{"name":"ansi-regex","version":"6.3.0","type":"module","exports":"./index.js","scripts":{"postinstall":"echo installed > /tmp/should-not-run"}}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"ansi-regex","version":"6.3.0","lockfileVersion":3,"packages":{"":{"name":"ansi-regex","version":"6.3.0","type":"module","hasInstallScript":true}}}
JSON
cat > /workspace/index.js <<'JS'
export default () => /ordinary/;
JS
