#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
printf '%s\n' '{"name":"strip-final-newline","version":"4.0.0","type":"module","exports":{"types":"./index.d.ts","default":"./index.js"},"scripts":{"postinstall":"echo should-not-run > /tmp/strip-final-newline-hook"}}' > /workspace/package.json
printf '%s\n' '{"name":"strip-final-newline","version":"4.0.0","lockfileVersion":3,"packages":{"":{"name":"strip-final-newline","version":"4.0.0","type":"module","hasInstallScript":true}}}' > /workspace/package-lock.json
printf '%s\n' 'export default input => input;' > /workspace/index.js
