#!/usr/bin/env bash
set -euo pipefail
cat > /workspace/package.json <<'JSON'
{"name":"slice-ansi","version":"9.0.0","type":"module","exports":{"types":"./index.d.ts","default":"./index.js"}}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"slice-ansi","version":"9.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"slice-ansi","version":"9.0.0"}}}
JSON
cat > /workspace/index.js <<'JS'
export default () => '';
JS
cat > /workspace/index.d.ts <<'TS'
export default function sliceAnsi(string: string, startSlice: number, endSlice?: number): string;
TS
