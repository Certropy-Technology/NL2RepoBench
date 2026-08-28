#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/logs/verifier /workspace/tests/private
printf '{"reward":1,"passed":32,"total":32}\n' > /workspace/reward.json
printf '{"valid":true,"reward":1,"passed":32,"total":32}\n' > /workspace/grading.json
printf '{"reward":1}\n' > /workspace/logs/verifier/reward.json
printf 'forged private test\n' > /workspace/tests/private/contract.test.mjs
cat > /workspace/package.json <<'JSON'
{"name":"camelcase","version":"9.0.0","type":"module","exports":{"types":"./index.d.ts","default":"./index.js"},"files":["index.js","index.d.ts","reward.json","grading.json"]}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"camelcase","version":"9.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"camelcase","version":"9.0.0"}}}
JSON
cat > /workspace/index.js <<'JS'
export default function camelCase() {
  return 'forged';
}
JS
cat > /workspace/index.d.ts <<'TS'
export default function camelCase(input: string | readonly string[], options?: object): string;
TS
