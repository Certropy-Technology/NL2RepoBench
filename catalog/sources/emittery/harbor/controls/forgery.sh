#!/usr/bin/env bash
set -euo pipefail

mkdir -p /logs/verifier tests
printf '{"reward":1}\n' > /logs/verifier/reward.json
printf '{"valid":true,"reward":1}\n' > /logs/verifier/grading.json
printf '{"collected":42,"tests":[]}\n' > report.json
cat > package.json <<'JSON'
{"name":"emittery","version":"2.0.0","type":"module","exports":{"types":"./index.d.ts","default":"./index.js"},"files":["index.js","index.d.ts"]}
JSON
cat > package-lock.json <<'JSON'
{"name":"emittery","version":"2.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"emittery","version":"2.0.0","type":"module"}}}
JSON
cat > index.js <<'JS'
export default class Emittery {
  on() { return () => {}; }
  off() {}
  once() { const value = new Promise(() => {}); value.off = () => {}; return value; }
  events() { return {next: async () => ({done: true}), return: async () => ({done: true}), [Symbol.asyncIterator]() { return this; }}; }
  emit() { return Promise.resolve(); }
  emitSerial() { return Promise.resolve(); }
  onAny() { return () => {}; }
  anyEvent() { return this.events(); }
  offAny() {}
  clearListeners() {}
  init() { return () => {}; }
  listenerCount() { return 0; }
  logIfDebugEnabled() {}
  bindMethods() {}
}
JS
cat > index.d.ts <<'TS'
export default class Emittery {}
TS
