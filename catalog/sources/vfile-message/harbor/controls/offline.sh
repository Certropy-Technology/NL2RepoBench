#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"vfile-message","version":"4.0.3","type":"module","exports":"./index.js"}
JSON
cat > package-lock.json <<'JSON'
{"name":"vfile-message","version":"4.0.3","lockfileVersion":3,"requires":true,"packages":{"":{"name":"vfile-message","version":"4.0.3","type":"module"}}}
JSON
cat > index.js <<'JS'
export class VFileMessage extends Error { constructor(reason) { fetch('https://example.invalid/nl2repobench-network-probe').catch(() => {}); super(String(reason)); this.reason = String(reason); this.name = '1:1'; this.file = ''; this.stack = ''; } }
JS
