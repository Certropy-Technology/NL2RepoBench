#!/usr/bin/env bash
set -euo pipefail
install -d -m 0755 /workspace
printf '%s\n' '{"name":"pino","version":"0.0.0","main":"index.js"}' > /workspace/package.json
printf '%s\n' 'module.exports = function () { return {}; }' > /workspace/index.js
printf '%s\n' '{"lockfileVersion":3,"packages":{"":{"name":"pino","version":"0.0.0"}}}' > /workspace/package-lock.json
