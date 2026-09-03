#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"deepmerge","version":"4.3.1","main":"missing.js"}
JSON
cat > package-lock.json <<'JSON'
{"name":"deepmerge","version":"4.3.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"deepmerge","version":"4.3.1"},"node_modules/unclosed":
JSON
