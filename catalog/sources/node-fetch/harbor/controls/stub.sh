#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
cat > /workspace/package.json <<'JSON'
{"name":"node-fetch","version":"3.1.1","type":"module","exports":"./index.js"}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"node-fetch","version":"3.1.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"node-fetch","version":"3.1.1","type":"module","exports":"./index.js"}}}
JSON
cat > /workspace/index.js <<'JS'
export const Headers = class {};
export const Request = class {};
export const Response = class {};
export const isRedirect = () => false;
export default async () => { throw new TypeError('stub'); };
JS
