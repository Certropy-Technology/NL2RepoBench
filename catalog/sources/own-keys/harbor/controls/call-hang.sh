#!/usr/bin/env bash
set -euo pipefail

cat > package.json <<'JSON'
{"name":"own-keys","version":"1.0.2","main":"index.js","exports":{".":"./index.js","./package.json":"./package.json"},"sideEffects":false,"license":"MIT"}
JSON
cat > package-lock.json <<'JSON'
{"name":"own-keys","version":"1.0.2","lockfileVersion":3,"requires":true,"packages":{"":{"name":"own-keys","version":"1.0.2","license":"MIT"}}}
JSON
cat > index.js <<'JS'
'use strict';
module.exports = function ownKeys(_source) {
  while (true) {}
};
JS
