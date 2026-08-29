#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/dist
cat > /workspace/package.json <<'JSON'
{"name":"fast-string-width","version":"3.0.2","type":"module","exports":"./dist/index.js","main":"./dist/index.js"}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"fast-string-width","version":"3.0.2","lockfileVersion":3,"requires":true,"packages":{"":{"name":"fast-string-width","version":"3.0.2","type":"module"}}}
JSON
node --input-type=module - <<'JS'
import {writeFileSync} from 'node:fs';
writeFileSync('/workspace/dist/index.js', `export default () => '${'x'.repeat(9_000_000)}';\n`);
JS
