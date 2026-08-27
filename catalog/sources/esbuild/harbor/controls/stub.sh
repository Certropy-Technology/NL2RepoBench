#!/usr/bin/env bash
set -euo pipefail

rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
mkdir -p /workspace/lib
cat > /workspace/package.json <<'JSON'
{
  "name": "esbuild",
  "version": "0.28.2",
  "main": "lib/entry.cjs",
  "license": "MIT"
}
JSON
cat > /workspace/package-lock.json <<'JSON'
{
  "name": "esbuild",
  "version": "0.28.2",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": {
      "name": "esbuild",
      "version": "0.28.2",
      "license": "MIT"
    }
  }
}
JSON
cat > /workspace/lib/entry.cjs <<'JS'
module.exports = require('./main.js');
JS
cat > /workspace/lib/main.js <<'JS'
const empty = () => ({ code: '', warnings: [], errors: [] });
module.exports = {
  transformSync: empty,
  buildSync: () => ({ outputFiles: [], warnings: [], errors: [] }),
  formatMessagesSync: () => [],
  analyzeMetafileSync: () => '',
};
JS
