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
await fetch('https://example.com/nl2repobench-network-must-be-blocked');
export const identity = value => value;
JS
cat > /workspace/dist/index.d.ts <<'TS'
export declare const identity: (value: unknown) => unknown;
TS
