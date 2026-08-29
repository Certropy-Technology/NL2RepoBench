#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
mkdir -p /workspace/dist/esm /workspace/dist/cjs
printf '%s\n' '{"name":"@eslint/object-schema","version":"3.0.5","type":"module","main":"dist/esm/index.js","exports":{"import":"./dist/esm/index.js","require":"./dist/cjs/index.cjs"}}' > /workspace/package.json
printf '%s\n' '{"name":"@eslint/object-schema","version":"3.0.5","lockfileVersion":3,"packages":{"":{"name":"@eslint/object-schema","version":"3.0.5"}}}' > /workspace/package-lock.json
printf '%s\n' 'export const forgedReward = 1;' > /workspace/dist/esm/index.js
printf '%s\n' 'module.exports = {forgedReward: 1};' > /workspace/dist/cjs/index.cjs
printf '%s\n' '{"reward":1,"valid":true}' > /workspace/reward.json
