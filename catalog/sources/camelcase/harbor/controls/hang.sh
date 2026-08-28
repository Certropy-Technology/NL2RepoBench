#!/usr/bin/env bash
set -euo pipefail

cat > /workspace/package.json <<'JSON'
{"name":"camelcase","version":"9.0.0","type":"module","exports":{"types":"./index.d.ts","default":"./index.js"},"files":["index.js","index.d.ts"]}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"camelcase","version":"9.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"camelcase","version":"9.0.0"}}}
JSON
cat > /workspace/index.js <<'JS'
export default function camelCase() {
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0);
}
JS
cat > /workspace/index.d.ts <<'TS'
export default function camelCase(input: string | readonly string[], options?: object): string;
TS
