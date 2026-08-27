#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"nanoid","version":"6.0.1","type":"module","exports":{".":{"import":"./index.js"},"./non-secure":{"import":"./non-secure/index.js"}}}
JSON
cat > package-lock.json <<'JSON'
{"name":"nanoid","version":"6.0.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"nanoid","version":"6.0.1","type":"module","exports":{".":{"import":"./index.js"},"./non-secure":{"import":"./non-secure/index.js"}}}}}
JSON
cat > index.js <<'JS'
export const urlAlphabet = 'x'
export const nanoid = async () => fetch('https://example.invalid/should-be-blocked')
export const customAlphabet = () => () => ''
export const customRandom = () => () => ''
export const random = () => new Uint8Array()
JS
mkdir -p non-secure
cat > non-secure/index.js <<'JS'
export const nanoid = () => ''
export const customAlphabet = () => () => ''
JS
