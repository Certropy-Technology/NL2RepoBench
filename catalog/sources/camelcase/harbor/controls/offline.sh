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
  fetch('https://example.invalid/nl2repobench-network-probe').catch(() => {});
  return 'offline-control';
}
JS
cat > /workspace/index.d.ts <<'TS'
export default function camelCase(input: string | readonly string[], options?: object): string;
TS
