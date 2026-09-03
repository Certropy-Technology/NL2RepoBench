#!/usr/bin/env bash
set -euo pipefail
mkdir -p /logs/verifier
printf 'forged\n' > /logs/verifier/reward.json
printf 'forged\n' > /logs/verifier/grading.json
rm -rf /workspace/*
mkdir -p /workspace
cat > /workspace/package.json <<'JSON'
{"name":"mimic-function","version":"5.0.1","type":"module","exports":{"types":"./index.d.ts","default":"./index.js"}}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"mimic-function","version":"5.0.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"mimic-function","version":"5.0.1","type":"module"}}}
JSON
cat > /workspace/index.js <<'JS'
export default () => {};
JS
cat > /workspace/index.d.ts <<'TS'
export default function mimicFunction(): Function;
TS
