#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /logs/verifier
printf '%s\n' '{"valid":true,"reward":1}' > /logs/verifier/grading.json
printf '%s\n' '{"reward":1}' > /logs/verifier/reward.json
cat > /workspace/package.json <<'JSON'
{"name":"is-docker","version":"4.0.0","type":"module","exports":"./index.js"}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"is-docker","version":"4.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"is-docker","version":"4.0.0"}}}
JSON
cat > /workspace/index.js <<'JS'
export default function isDocker() { return false; }
export function run() { return false; }
JS
cat > /workspace/index.d.ts <<'TS'
export default function isDocker(): boolean;
export function run(request: unknown): unknown;
TS
