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
module.exports = { createWarning: () => () => false, createDeprecation: () => () => false, spyWarning: () => ({ calls: [], callCount: () => 0, reset: () => {}, restore: () => {} }) }
JS
mkdir -p types
printf '%s\n' 'export = processWarning;' > types/index.d.ts
