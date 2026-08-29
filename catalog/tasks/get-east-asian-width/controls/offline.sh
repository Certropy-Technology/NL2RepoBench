#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"get-east-asian-width","version":"1.6.0","type":"module","exports":{".":"./index.js"}}
JSON
cat > package-lock.json <<'JSON'
{"name":"get-east-asian-width","version":"1.6.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"get-east-asian-width","version":"1.6.0","type":"module"}}}
JSON
cat > index.js <<'JS'
export const eastAsianWidth = async () => fetch('https://example.invalid/should-be-blocked');
export const eastAsianWidthType = () => 'neutral';
JS
