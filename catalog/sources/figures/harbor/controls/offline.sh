#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"figures","version":"6.1.0","type":"module","exports":{"types":"./index.d.ts","default":"./index.js"}}
JSON
cat > package-lock.json <<'JSON'
{"name":"figures","version":"6.1.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"figures","version":"6.1.0","type":"module"}}}
JSON
cat > index.js <<'JS'
export const replaceSymbols = async () => fetch('https://example.invalid/blocked');
export const mainSymbols = {};
export const fallbackSymbols = {};
export default {replaceSymbols, mainSymbols, fallbackSymbols};
JS
