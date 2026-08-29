#!/usr/bin/env bash
set -euo pipefail
cat > /workspace/package.json <<'JSON'
{"name":"safe-stable-stringify","version":"0.0.0","main":"index.js","scripts":{"postinstall":"echo forbidden"}}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"safe-stable-stringify","version":"0.0.0","lockfileVersion":3,"packages":{"":{"name":"safe-stable-stringify","version":"0.0.0","scripts":{"postinstall":"echo forbidden"}}}}
JSON
printf '%s\n' 'module.exports = () => "install-script";' > /workspace/index.js
