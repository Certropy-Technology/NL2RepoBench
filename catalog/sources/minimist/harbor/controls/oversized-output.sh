#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"minimist","version":"2.0.0","main":"index.js"}
JSON
cat > package-lock.json <<'JSON'
{"name":"minimist","version":"2.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"minimist","version":"2.0.0"}}}
JSON
cat > index.js <<'JS'
module.exports = function () { return 'x'.repeat(300_000); };
JS
