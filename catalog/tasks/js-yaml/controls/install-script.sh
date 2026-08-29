#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"js-yaml","version":"5.4.0","type":"module","scripts":{"postinstall":"echo forbidden"},"exports":{".":{"import":"./index.mjs"},"./package.json":"./package.json"}}
JSON
cat > package-lock.json <<'JSON'
{"name":"js-yaml","version":"5.4.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"js-yaml","version":"5.4.0","type":"module","scripts":{"postinstall":"echo forbidden"},"dependencies":{}}}}
JSON
cat > index.mjs <<'JS'
export const load = () => null;
export const loadAll = () => [];
export const dump = () => "";
JS
