#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"get-east-asian-width","version":"1.6.0","type":"module","scripts":{"postinstall":"echo forbidden"},"exports":{".":"./index.js"}}
JSON
cat > package-lock.json <<'JSON'
{"name":"get-east-asian-width","version":"1.6.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"get-east-asian-width","version":"1.6.0","type":"module","scripts":{"postinstall":"echo forbidden"}}}}
JSON
cat > index.js <<'JS'
export const eastAsianWidth = () => 1;
export const eastAsianWidthType = () => 'neutral';
JS
