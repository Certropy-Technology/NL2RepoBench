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
  #resolve; #reject; #state = "pending"; #reason;
  constructor(executor = null) { let r, j; super((resolve, reject) => { r=resolve; j=reject; executor?.(resolve, reject); }); this.#resolve = r; this.#reject = j; }
  get state() { return this.#state; }
  get rejectionReason() { return this.#reason; }
  resolve(value) { if (this.#state === "pending") { this.#state = "fulfilled"; this.#resolve(value); } }
  reject(reason) { if (this.#state === "pending") { this.#state = "rejected"; this.#reason = reason; this.#reject(reason); } }
}
export function createDeferredExecutor() { let r, j, state="pending", reason; const e=(resolve,reject)=>{r=resolve;j=reject;}; e.resolve=v=>{if(state!=="pending")return;state="fulfilled";r(v)}; e.reject=x=>{if(state!=="pending")return;state="rejected";reason=x;j(x)}; Object.defineProperties(e,{state:{get:()=>state},rejectionReason:{get:()=>reason}}); return e; }
JS
cat > /workspace/build/index.d.mts <<'TS'
export declare class DeferredPromise<T = unknown> extends Promise<T> { readonly state: string; readonly rejectionReason: unknown; resolve(value?: T): void; reject(reason?: unknown): void; }
export declare function createDeferredExecutor<T = never>(): unknown;
TS
