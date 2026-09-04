#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/dist
cat > /workspace/package.json <<'JSON'
{"name":"remeda","version":"2.0.0","type":"module","exports":{".":{"import":"./dist/index.js"}}}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"remeda","version":"2.0.0","lockfileVersion":3,"packages":{"":{"name":"remeda","version":"2.0.0","type":"module"}}}
JSON
cat > /workspace/dist/index.js <<'JS'
export const identity = value => { while (true) {} };
JS
cat > /workspace/dist/index.d.ts <<'TS'
export declare const identity: (value: unknown) => unknown;
TS
