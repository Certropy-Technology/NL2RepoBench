#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"is-string","version":"1.1.1","main":"index.js","types":"index.d.ts"}
JSON
cat > package-lock.json <<'JSON'
{"name":"is-string","version":"1.1.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"is-string","version":"1.1.1"}}}
JSON
printf '%s\n' "module.exports = {};" > index.js
