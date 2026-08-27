#!/usr/bin/env bash
set -euo pipefail

rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
cat > /workspace/package.json <<'JSON'
{"name":"prettier","version":"3.10.0-dev","type":"commonjs","scripts":{"postinstall":"node -e 'process.exit(0)'"},"exports":{".":{"types":"./index.d.ts","default":"./index.mjs"}}}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"prettier","version":"3.10.0-dev","lockfileVersion":3,"requires":true,"packages":{"":{"name":"prettier","version":"3.10.0-dev","type":"commonjs"}}}
JSON
printf "export const version = '3.10.0-dev';\n" > /workspace/index.mjs
printf 'export declare const version: string;\n' > /workspace/index.d.ts
