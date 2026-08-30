#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
cat > /workspace/package.json <<'JSON'
{"name":"pretty-ms","version":"9.3.0","type":"module","exports":{"types":"./index.d.ts","default":"./index.js"},"dependencies":{"parse-ms":"4.0.0"}}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"pretty-ms","version":"9.3.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"pretty-ms","version":"9.3.0","dependencies":{"parse-ms":"4.0.0"}},"node_modules/parse-ms":{"version":"4.0.0","resolved":"https://registry.npmjs.org/parse-ms/-/parse-ms-4.0.0.tgz","integrity":"sha512-TXfryirbmq34y8QBwgqCVLi+8oA3oWx2eAnSn62ITyEhEYaWRlVZ2DvMM9eZbMs/RfxPu/PK/aBLyGj4IrqMHw=="}}}
JSON
cat > /workspace/index.js <<'JS'
export default function prettyMilliseconds() { return 'stub'; }
JS
