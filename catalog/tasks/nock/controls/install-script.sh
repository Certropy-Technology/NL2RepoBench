#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cat > /workspace/package.json <<'JSON'
{"name":"nock","version":"0.0.0-development","main":"index.js","license":"MIT","scripts":{"postinstall":"node -e \"for (;;) {}\""}}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"nock","version":"0.0.0-development","lockfileVersion":3,"requires":true,"packages":{"":{"name":"nock","version":"0.0.0-development","license":"MIT","hasInstallScript":true}}}
JSON
cat > /workspace/index.js <<'JS'
module.exports = function nock() { return {}; };
JS
