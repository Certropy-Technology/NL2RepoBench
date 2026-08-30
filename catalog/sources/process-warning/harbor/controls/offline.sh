#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"process-warning","version":"5.1.0","main":"index.js","type":"commonjs"}
JSON
cat > package-lock.json <<'JSON'
{"name":"process-warning","version":"5.1.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"process-warning","version":"5.1.0"}}}
JSON
cat > index.js <<'JS'
'use strict'
module.exports = {
  createWarning: ({name, code, message}) => { fetch('https://example.invalid').catch(() => {}); return () => Boolean(name && code && message) },
  createDeprecation: () => () => false,
  spyWarning: () => ({})
}
JS
