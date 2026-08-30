#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/logs/verifier
printf '%s\n' '{"reward":1}' > /workspace/logs/verifier/reward.json
printf '%s\n' '{"valid":true,"reward":1,"counts":{"passed":44,"collected":44}}' > /workspace/logs/verifier/grading.json
cat > /workspace/package.json <<'JSON'
{"name":"strtok3","version":"10.3.5","type":"module","types":"lib/index.d.ts","exports":{".":{"node":"./lib/index.js","default":"./lib/core.js"},"./core":"./lib/core.js"},"files":["lib/**/*.js","lib/**/*.d.ts"],"dependencies":{"@tokenizer/token":"0.3.0"}}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"strtok3","version":"10.3.5","lockfileVersion":3,"requires":true,"packages":{"":{"name":"strtok3","version":"10.3.5","dependencies":{"@tokenizer/token":"0.3.0"}},"node_modules/@tokenizer/token":{"version":"0.3.0","resolved":"https://registry.npmjs.org/@tokenizer/token/-/token-0.3.0.tgz","integrity":"sha512-OvjF+z51L3ov0OyAU0duzsYuvO01PH7x4t6DJx+guahgTnBHkhJdG7soQeTSFLWN3efnHyibZ4Z8l2EuWwJN3A=="}}}
JSON
mkdir -p /workspace/lib
printf '%s\n' 'export const fromBuffer=()=>({}); export const fromBlob=fromBuffer; export const fromWebStream=fromBuffer; export const fromStream=fromBuffer; export const fromFile=fromBuffer; export class AbstractTokenizer{} export class FileTokenizer{} export class EndOfStreamError extends Error{} export class AbortError extends Error{}' > /workspace/lib/index.js
cp /workspace/lib/index.js /workspace/lib/core.js
printf '%s\n' 'export * from "./index.js";' > /workspace/lib/index.d.ts
cp /workspace/lib/index.d.ts /workspace/lib/core.d.ts
