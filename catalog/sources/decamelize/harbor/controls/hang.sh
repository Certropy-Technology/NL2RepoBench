#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cat > /workspace/package.json <<'JSON'
{"name":"decamelize","version":"6.0.1","type":"module","exports":"./index.js"}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"decamelize","version":"6.0.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"decamelize","version":"6.0.1"}}}
JSON
cat > /workspace/index.js <<'JS'
Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, 60_000);
JS
