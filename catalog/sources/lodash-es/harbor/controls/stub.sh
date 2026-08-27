#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
cat > /workspace/package.json <<'JSON'
{"name":"lodash-es","version":"4.18.1","type":"module","exports":{".":"./index.js"}}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"lodash-es","version":"4.18.1","lockfileVersion":3,"packages":{"":{"name":"lodash-es","version":"4.18.1"}}}
JSON
cat > /workspace/index.js <<'JS'
export const chunk = (value) => value;
JS
