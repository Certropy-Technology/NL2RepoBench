#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/dist
cat > /workspace/package.json <<'JSON'
{"name":"cross-fetch","version":"4.1.0","main":"dist/node-ponyfill.js","files":["dist/node-ponyfill.js"]}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"cross-fetch","version":"4.1.0","lockfileVersion":3,"packages":{"":{"name":"cross-fetch","version":"4.1.0"}}}
JSON
cat > /workspace/dist/node-ponyfill.js <<'JS'
const fetch = () => globalThis.fetch('https://example.invalid/nl2repobench-network-probe');
fetch.fetch = fetch;
fetch.default = fetch;
module.exports = fetch;
JS
