#!/usr/bin/env bash
set -euo pipefail
cat > /workspace/package.json <<'JSON'
{"name":"widest-line","version":"6.0.0","scripts":{"install":"touch /tmp/should-not-run"},"type":"module","exports":{"types":"./index.d.ts","default":"./index.js"},"files":["index.js","index.d.ts"]}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"widest-line","version":"6.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"widest-line","version":"6.0.0","hasInstallScript":true}}}
JSON
cat > /workspace/index.js <<'JS'
export default function widestLine() { return 0; }
JS
cat > /workspace/index.d.ts <<'TS'
export default function widestLine(string: string): number;
TS
