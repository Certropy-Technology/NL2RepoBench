#!/usr/bin/env bash
set -euo pipefail
cat > /workspace/package.json <<'JSON'
{"name":"widest-line","version":"6.0.0","type":"module","exports":{"types":"./index.d.ts","default":"./index.js"},"files":["index.js","index.d.ts"]}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"widest-line","version":"6.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"widest-line","version":"6.0.0"}}}
JSON
cat > /workspace/index.js <<'JS'
export default function widestLine() { return import('node:fs').then(() => 0); }
JS
cat > /workspace/index.d.ts <<'TS'
export default function widestLine(string: string): Promise<number>;
TS
