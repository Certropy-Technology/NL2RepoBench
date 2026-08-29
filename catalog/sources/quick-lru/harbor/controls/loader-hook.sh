#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
printf '%s\n' '{"name":"quick-lru","version":"7.3.0","type":"module","exports":{"default":"./index.js"},"files":["index.js"]}' > /workspace/package.json
printf '%s\n' '{"name":"quick-lru","version":"7.3.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"quick-lru","version":"7.3.0"}}}' > /workspace/package-lock.json
printf '%s\n' 'export default class QuickLRU extends Map {}' > /workspace/index.js
printf '%s\n' 'export default class QuickLRU {}' > /workspace/index.d.ts
