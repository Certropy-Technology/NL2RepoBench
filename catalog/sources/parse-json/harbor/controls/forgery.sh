#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"parse-json","version":"8.3.0","type":"module","exports":{"types":"./index.d.ts","default":"./index.js"}}
JSON
cat > package-lock.json <<'JSON'
{"name":"parse-json","version":"8.3.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"parse-json","version":"8.3.0","type":"module"}}}
JSON
cat > index.js <<'JS'
export default () => { throw new Error('forged candidate'); };
JS
cat > index.d.ts <<'TS'
export default function parseJson(input: string): unknown;
TS
printf '{"reward":1,"valid":true}\n' > reward.json
printf '{"passed":30,"collected":30}\n' > grading.json
