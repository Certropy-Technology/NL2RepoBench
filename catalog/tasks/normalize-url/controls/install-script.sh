#!/usr/bin/env bash
set -euo pipefail
cat > /workspace/package.json <<'JSON'
{"name":"normalize-url","version":"9.0.1","type":"module","exports":{"types":"./index.d.ts","default":"./index.js"},"scripts":{"postinstall":"node -e \"process.exit(99)\""}}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"normalize-url","version":"9.0.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"normalize-url","version":"9.0.1","scripts":{"postinstall":"node -e \"process.exit(99)\""}}}}
JSON
cat > /workspace/index.js <<'JS'
export default () => '';
JS
cat > /workspace/index.d.ts <<'TS'
export default function normalizeUrl(url: string, options?: object): string;
TS
