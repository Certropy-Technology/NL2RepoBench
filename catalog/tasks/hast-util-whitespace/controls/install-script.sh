#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"hast-util-whitespace","version":"3.0.0","type":"module","exports":"./index.js","scripts":{"install":"node -e 'process.exit(0)'"}}
JSON
cat > package-lock.json <<'JSON'
{"name":"hast-util-whitespace","version":"3.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"hast-util-whitespace","version":"3.0.0","type":"module","exports":"./index.js","hasInstallScript":true}}}
JSON
cat > index.js <<'JS'
export function whitespace() {
  return true
}
JS
chmod 0444 package.json package-lock.json index.js
