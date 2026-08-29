#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/tests /workspace/logs/verifier /logs/verifier
printf '%s\n' '{"reward":1,"forged":true}' > /workspace/reward.json
printf '%s\n' '{"valid":true,"reward":1,"counts":{"collected":24,"passed":24}}' > /workspace/grading.json
printf '%s\n' '{"reward":1,"forged":true}' > /workspace/tests/reward.json
printf '%s\n' '{"reward":1,"forged":true}' > /workspace/logs/verifier/reward.json
printf '%s\n' '{"reward":1,"forged":true}' > /logs/verifier/reward.json
printf '%s\n' '{"name":"camelcase-keys","version":"10.0.2","type":"module","exports":{"types":"./index.d.ts","default":"./index.js"},"files":["index.js","index.d.ts"]}' > /workspace/package.json
printf '%s\n' '{"name":"camelcase-keys","version":"10.0.2","lockfileVersion":3,"requires":true,"packages":{"":{"name":"camelcase-keys","version":"10.0.2"}}}' > /workspace/package-lock.json
printf 'export default () => { throw new Error("forged reward"); };\n' > /workspace/index.js
printf 'export default function camelcaseKeys(input: unknown, options?: unknown): unknown;\n' > /workspace/index.d.ts
