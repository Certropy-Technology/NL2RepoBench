#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"deepmerge","version":"4.3.1","main":"index.js"}
JSON
cat > index.js <<'JS'
const {closeSync, openSync} = require('node:fs');
module.exports = () => {
  const sentinel = '/tmp/candidate-site/tmp/deepmerge-hang-once';
  try { closeSync(openSync(sentinel, 'wx')); } catch { throw new Error('bounded hang follow-up'); }
  while (true) {}
};
JS
cat > package-lock.json <<'JSON'
{"name":"deepmerge","version":"4.3.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"deepmerge","version":"4.3.1"}}}
JSON
