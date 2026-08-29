#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"has-ansi","version":"6.0.2","type":"module","exports":{".":{"default":"./index.js"}}}
JSON
cat > index.js <<'JS'
export default async () => fetch('https://example.invalid/should-be-blocked');
JS
cat > package-lock.json <<'JSON'
{"name":"has-ansi","version":"6.0.2","lockfileVersion":3,"requires":true,"packages":{"":{"name":"has-ansi","version":"6.0.2"}}}
JSON
