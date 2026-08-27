#!/usr/bin/env bash
set -euo pipefail

rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
cat > /workspace/package.json <<'JSON'
{
  "name": "execa",
  "version": "10.0.1",
  "type": "module",
  "scripts": {"postinstall": "printf forbidden > /workspace/install-script-ran"},
  "exports": {".": {"import": "./index.js", "default": "./index.js"}}
}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"execa","version":"10.0.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"execa","version":"10.0.1","type":"module","hasInstallScript":true}}}
JSON
printf 'export const execa = () => {};\n' > /workspace/index.js

