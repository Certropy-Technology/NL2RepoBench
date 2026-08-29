#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
printf '%s\n' '{"name":"json-stable-stringify","version":"0.0.0","main":"index.js","scripts":{"preinstall":"node -e \\"process.exit(1)\\""}}' > /workspace/package.json
printf '%s\n' '{"name":"json-stable-stringify","version":"0.0.0","lockfileVersion":3,"packages":{"":{"name":"json-stable-stringify","version":"0.0.0","hasInstallScript":true}}}' > /workspace/package-lock.json
printf '%s\n' 'module.exports = function () { return "bad"; };' > /workspace/index.js
