#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/build
cat > /workspace/package.json <<'JSON'
{"name":"@open-draft/deferred-promise","version":"3.0.0","type":"module","exports":{".":"./build/index.mjs"},"files":["build"]}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"@open-draft/deferred-promise","version":"3.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"@open-draft/deferred-promise","version":"3.0.0"}}}
JSON
cat > /workspace/build/index.mjs <<'JS'
export class DeferredPromise extends Promise { constructor() { super(() => {}); } resolve() { return new Promise(() => {}); } reject() {} }
export function createDeferredExecutor() { return () => new Promise(() => {}); }
JS
sleep 3600
