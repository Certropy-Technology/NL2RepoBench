#!/usr/bin/env bash
set -euo pipefail

cat > package.json <<'JSON'
{"name":"mdast-util-phrasing","version":"4.1.0","type":"module","exports":"./index.js"}
JSON
cat > package-lock.json <<'JSON'
{"name":"mdast-util-phrasing","version":"4.1.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"mdast-util-phrasing","version":"4.1.0","type":"module"}}}
JSON
cat > index.js <<'JS'
export function phrasing() {
  throw new Error('not implemented')
}
JS
