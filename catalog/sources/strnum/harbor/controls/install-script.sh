#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cat > /workspace/package.json <<'JSON'
{"name":"strnum","version":"2.4.2","type":"module","main":"strnum.js","scripts":{"postinstall":"echo forbidden"}}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"strnum","version":"2.4.2","lockfileVersion":3,"requires":true,"packages":{"":{"name":"strnum","version":"2.4.2","hasInstallScript":true}}}
JSON
printf '%s\n' 'export default function toNumber() { return 0; }' > /workspace/strnum.js
