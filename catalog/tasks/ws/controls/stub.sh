#!/usr/bin/env bash
set -euo pipefail

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
