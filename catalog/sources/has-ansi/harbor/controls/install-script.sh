#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"has-ansi","version":"6.0.2","type":"module","scripts":{"postinstall":"echo forbidden"},"exports":{".":{"default":"./index.js"}}}
JSON
cat > index.js <<'JS'
export default () => false;
JS
cat > package-lock.json <<'JSON'
{"name":"has-ansi","version":"6.0.2","lockfileVersion":3,"requires":true,"packages":{"":{"name":"has-ansi","version":"6.0.2"}}}
JSON
