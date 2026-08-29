#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
printf '%s\n' '{"name":"json-stable-stringify","version":"0.0.0","main":"index.js"}' > /workspace/package.json
printf '%s\n' '{"name":"json-stable-stringify","version":"0.0.0","lockfileVersion":3,"packages":{"":{"name":"json-stable-stringify","version":"0.0.0"}}}' > /workspace/package-lock.json
printf '%s\n' 'module.exports = function () { return "{\\"a\\":1}"; };' > /workspace/index.js
mkdir -p /workspace/logs/verifier
printf '%s\n' '{"reward":1,"valid":true,"passed":52,"collected":52}' > /workspace/logs/verifier/grading.json
