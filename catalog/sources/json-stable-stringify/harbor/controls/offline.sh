#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
printf '%s\n' '{"name":"json-stable-stringify","version":"0.0.0","main":"index.js"}' > /workspace/package.json
printf '%s\n' '{"name":"json-stable-stringify","version":"0.0.0","lockfileVersion":3,"packages":{"":{"name":"json-stable-stringify","version":"0.0.0"}}}' > /workspace/package-lock.json
printf '%s\n' 'module.exports = function (value) { return JSON.stringify(value); };' > /workspace/index.js
