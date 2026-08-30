#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"wrong-package","version":"1.0.0","type":"module","exports":{"default":"./index.js"}}
JSON
cat > package-lock.json <<'JSON'
{"name":"wrong-package","version":"1.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"wrong-package","version":"1.0.0"}}}
JSON
printf 'export default () => 0;\n' > index.js
printf 'export default function stringWidth(string: string): number;\n' > index.d.ts
