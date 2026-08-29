#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/dist
printf '%s\n' '{"name":"basic-ftp","version":"6.2.0","main":"dist/index.js"}' > /workspace/package.json
printf '%s\n' '{"name":"basic-ftp","version":"6.2.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"basic-ftp","version":"6.2.0"}}}' > /workspace/package-lock.json
printf '%s\n' 'require("https").get("https://example.com/nl2repobench-network-must-be-blocked"); module.exports = {};' > /workspace/dist/index.js
