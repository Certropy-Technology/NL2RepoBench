#!/usr/bin/env bash
set -euo pipefail

rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
mkdir -p /workspace/dist/bin /workspace/dist/es /workspace/dist/wasm-node

cat > /workspace/package.json <<'JSON'
{
  "name": "rollup",
  "version": "4.62.5",
  "description": "stub control",
  "main": "dist/rollup.js",
  "types": "dist/rollup.d.ts",
  "bin": { "rollup": "dist/bin/rollup" },
  "exports": {
    ".": {
      "types": "./dist/rollup.d.ts",
      "require": "./dist/rollup.js",
      "import": "./dist/es/rollup.js"
    }
  },
  "files": ["dist/**/*.js", "dist/**/*.d.ts", "dist/bin/rollup", "dist/wasm-node/*.wasm"],
  "license": "MIT"
}
JSON

cat > /workspace/package-lock.json <<'JSON'
{
  "name": "rollup",
  "version": "4.62.5",
  "lockfileVersion": 3,
  "requires": true,
  "packages": { "": { "name": "rollup", "version": "4.62.5" } }
}
JSON

cat > /workspace/dist/rollup.js <<'JS'
"use strict";
module.exports = {
  VERSION: "4.62.5",
  rollup: async () => { throw new Error("stub control"); },
  watch: () => { throw new Error("stub control"); },
  defineConfig: config => config,
};
JS

cat > /workspace/dist/es/rollup.js <<'JS'
export const VERSION = "4.62.5";
export const rollup = async () => { throw new Error("stub control"); };
export const watch = () => { throw new Error("stub control"); };
export const defineConfig = config => config;
JS

cat > /workspace/dist/rollup.d.ts <<'TS'
export declare const VERSION: string;
export declare function rollup(...args: any[]): Promise<never>;
export declare function watch(...args: any[]): never;
export declare function defineConfig<T>(config: T): T;
TS

cat > /workspace/dist/bin/rollup <<'JS'
#!/usr/bin/env node
process.stderr.write("stub control\n");
process.exitCode = 1;
JS
chmod 0755 /workspace/dist/bin/rollup
printf 'stub wasm\n' > /workspace/dist/wasm-node/bindings_wasm_bg.wasm
