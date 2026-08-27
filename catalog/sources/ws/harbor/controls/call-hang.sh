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
while (true) {}
JS
cat > wrapper.mjs <<'JS'
await new Promise(() => {});
JS
cat > browser.js <<'JS'
'use strict';
while (true) {}
JS
