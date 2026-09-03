#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"minimist","version":"2.0.0","main":"index.js"}
JSON
cat > package-lock.json <<'JSON'
{"name":"minimist","version":"2.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"minimist","version":"2.0.0"}}}
JSON
cat > index.js <<'JS'
module.exports = function () {
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, 60_000);
};
JS
