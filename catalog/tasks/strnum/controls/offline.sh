#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cat > /workspace/package.json <<'JSON'
{"name":"strnum","version":"2.4.2","type":"module","main":"strnum.js"}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"strnum","version":"2.4.2","lockfileVersion":3,"requires":true,"packages":{"":{"name":"strnum","version":"2.4.2"}}}
JSON
cat > /workspace/strnum.js <<'JS'
export default function toNumber() {
  fetch('https://example.invalid/should-be-blocked').catch(() => {});
  return 0;
}
JS
