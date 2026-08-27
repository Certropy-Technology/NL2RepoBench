#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/build
cat > /workspace/package.json <<'JSON'
{"name":"@open-draft/deferred-promise","version":"3.0.0","type":"module","exports":{".":{"types":"./build/index.d.mts","default":"./build/index.mjs"}},"files":["build"]}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"@open-draft/deferred-promise","version":"3.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"@open-draft/deferred-promise","version":"3.0.0"}}}
JSON
cat > /workspace/build/index.mjs <<'JS'
export class DeferredPromise extends Promise {
  constructor() { super(() => {}); this.state = "pending"; }
  resolve() {}
  reject() {}
}
export function createDeferredExecutor() { return () => {}; }
JS
cat > /workspace/build/index.d.mts <<'TS'
export declare class DeferredPromise<T = unknown> extends Promise<T> { resolve(value?: T): void; reject(reason?: unknown): void; }
export declare function createDeferredExecutor<T = never>(): ((resolve?: (value?: T) => void, reject?: (reason?: unknown) => void) => void) & { state: string; resolve(value?: T): void; reject(reason?: unknown): void };
TS
