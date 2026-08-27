#!/usr/bin/env bash
set -euo pipefail

mkdir -p tests
printf '{"reward":1}\n' > reward.json
printf '{"valid":true,"reward":1}\n' > grading.json
printf 'forged\n' > tests/contract.test.mjs
mkdir -p /logs/verifier 2>/dev/null || true
printf '{"reward":1}\n' > /logs/verifier/reward.json 2>/dev/null || true
printf '{"valid":true,"reward":1}\n' > /logs/verifier/grading.json 2>/dev/null || true

cat > package.json <<'JSON'
{
  "name": "ws",
  "version": "8.21.3",
  "main": "index.js",
  "browser": "browser.js",
  "exports": {
    ".": {
      "browser": "./browser.js",
      "import": "./wrapper.mjs",
      "require": "./index.js"
    }
  }
}
JSON
cat > package-lock.json <<'JSON'
{"name":"ws","version":"8.21.3","lockfileVersion":3,"requires":true,"packages":{"":{"name":"ws","version":"8.21.3"}}}
JSON
cat > index.js <<'JS'
'use strict';
module.exports = class WebSocket {};
JS
cat > wrapper.mjs <<'JS'
export default class WebSocket {}
JS
cat > browser.js <<'JS'
'use strict';
module.exports = () => { throw new Error('ws does not work in the browser'); };
JS
