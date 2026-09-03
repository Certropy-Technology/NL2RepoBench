#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"npm-run-path","version":"6.0.0","type":"module","exports":{"types":"./index.d.ts","default":"./index.js"},"files":["index.js","index.d.ts"]}
JSON
cat > package-lock.json <<'JSON'
{"name":"npm-run-path","version":"6.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"npm-run-path","version":"6.0.0"}}}
JSON
cat > index.js <<'JS'
const hang = () => { while (true) {} };
export const npmRunPath = hang;
export const npmRunPathEnv = hang;
JS
: > index.d.ts
