#!/usr/bin/env bash
set -euo pipefail

rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
cat > /workspace/package.json <<'JSON'
{"name":"execa","version":"10.0.1","type":"module","exports":{".":{"import":"./index.js","default":"./index.js"}}}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"execa","version":"10.0.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"execa","version":"10.0.1","type":"module"}}}
JSON
cat > /workspace/index.js <<'JS'
const hang = () => { while (true) {} };
export const execa = hang;
export const execaSync = hang;
export const execaNode = hang;
export const parseCommandString = hang;
export class ExecaError extends Error {}
export class ExecaSyncError extends Error {}
JS

