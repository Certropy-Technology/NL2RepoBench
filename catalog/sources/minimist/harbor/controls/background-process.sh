#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"minimist","version":"2.0.0","main":"index.js"}
JSON
cat > package-lock.json <<'JSON'
{"name":"minimist","version":"2.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"minimist","version":"2.0.0"}}}
JSON
cat > index.js <<'JS'
const {spawn} = require('node:child_process');
module.exports = function () {
  const child = spawn(process.execPath, ['-e', 'setInterval(() => {}, 1000)'], {
    detached: true,
    stdio: 'ignore',
  });
  child.unref();
  throw new Error('background-process control');
};
JS
