#!/usr/bin/env bash
set -euo pipefail

rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
cat > /workspace/package.json <<'JSON'
{"name":"better-sqlite3","version":"13.0.3","main":"index.js","type":"commonjs","scripts":{}}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"better-sqlite3","version":"13.0.3","lockfileVersion":3,"requires":true,"packages":{"":{"name":"better-sqlite3","version":"13.0.3"}}}
JSON
cat > /workspace/index.js <<'JS'
'use strict';
module.exports = function Database() {};
module.exports.runScenario = () => null;
JS
