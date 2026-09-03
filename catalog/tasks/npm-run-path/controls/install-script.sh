#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"npm-run-path","version":"6.0.0","type":"module","exports":{"types":"./index.d.ts","default":"./index.js"},"files":["index.js","index.d.ts"],"scripts":{"postinstall":"touch /tmp/forbidden-install-script"}}
JSON
cat > package-lock.json <<'JSON'
{"name":"npm-run-path","version":"6.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"npm-run-path","version":"6.0.0","hasInstallScript":true}}}
JSON
cat > index.js <<'JS'
export const npmRunPath = options => options?.path ?? '';
export const npmRunPathEnv = ({env = {}} = {}) => ({...env});
JS
: > index.d.ts
