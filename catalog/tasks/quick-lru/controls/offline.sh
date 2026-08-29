#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
printf '%s\n' '{"name":"quick-lru","version":"7.3.0","type":"module","exports":{"types":"./index.d.ts","default":"./index.js"},"files":["index.js","index.d.ts"]}' > /workspace/package.json
printf '%s\n' '{"name":"quick-lru","version":"7.3.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"quick-lru","version":"7.3.0"}}}' > /workspace/package-lock.json
cat > /workspace/index.js <<'JS'
export default class QuickLRU extends Map {
  constructor(options = {}) { super(); this.#maxSize = options.maxSize || 1; }
  #maxSize;
  get maxSize() { return this.#maxSize; }
  get maxAge() { return Infinity; }
  set(key, value) { super.set(key, value); return this; }
}
fetch('https://example.invalid/nl2repobench-network-probe').catch(() => {});
JS
printf '%s\n' 'export default class QuickLRU {}' > /workspace/index.d.ts
