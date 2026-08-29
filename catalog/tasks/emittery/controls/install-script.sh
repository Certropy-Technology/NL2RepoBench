#!/usr/bin/env bash
set -euo pipefail

cat > package.json <<'JSON'
{"name":"emittery","version":"2.0.0","type":"module","scripts":{"postinstall":"echo forbidden"},"exports":"./index.js"}
JSON
cat > package-lock.json <<'JSON'
{"name":"emittery","version":"2.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"emittery","version":"2.0.0","type":"module","hasInstallScript":true}}}
JSON
printf 'export default class Emittery {}\n' > index.js
