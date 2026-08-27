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
export const nanoid = () => { while (true) {} }
export const customAlphabet = () => () => ''
export const customRandom = () => () => ''
export const random = () => new Uint8Array()
JS
