#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"is-fullwidth-code-point","version":"5.1.0","type":"module","scripts":{"postinstall":"echo forbidden"},"exports":"./index.js"}
JSON
cat > package-lock.json <<'JSON'
{"name":"is-fullwidth-code-point","version":"5.1.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"is-fullwidth-code-point","version":"5.1.0"}}}
JSON
cat > index.js <<'JS'
export default () => false;
JS
cat > index.d.ts <<'TS'
export default function isFullwidthCodePoint(codePoint: number): boolean;
TS
