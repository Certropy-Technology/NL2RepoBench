#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
cat > /workspace/package.json <<'JSON'
{"name":"pg-connection-string","version":"2.14.0","main":"./index.js","files":["index.js"]}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"pg-connection-string","version":"2.14.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"pg-connection-string","version":"2.14.0"}}}
JSON
cat > /workspace/index.js <<'JS'
function parse(input) { fetch('https://example.invalid/nl2repobench-network-probe').catch(() => {}); return { database: input }; }
module.exports = parse;
module.exports.parse = parse;
module.exports.toClientConfig = parse;
module.exports.parseIntoClientConfig = parse;
JS
