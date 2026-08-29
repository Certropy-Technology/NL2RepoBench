#!/usr/bin/env bash
set -euo pipefail

cat > /workspace/package.json <<'JSON'
{"name":"flatted","version":"3.4.4","type":"module","main":"./cjs/index.cjs","exports":{".":{"types":"./types/index.d.ts","import":"./esm/index.js","default":"./cjs/index.cjs"}},"types":"./types/index.d.ts","files":["esm","cjs","types"]}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"flatted","version":"3.4.4","lockfileVersion":3,"requires":true,"packages":{"":{"name":"flatted","version":"3.4.4"}}}
JSON
mkdir -p /workspace/esm /workspace/cjs /workspace/types
cat > /workspace/esm/index.js <<'JS'
const hang = () => Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0);
export const stringify = hang;
export const parse = hang;
export const toJSON = hang;
export const fromJSON = hang;
JS
cat > /workspace/cjs/index.cjs <<'JS'
const hang = () => Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0);
exports.stringify = hang;
exports.parse = hang;
exports.toJSON = hang;
exports.fromJSON = hang;
JS
cat > /workspace/types/index.d.ts <<'TS'
export function parse(text: string, reviver?: (this: any, key: string, value: any) => any): any;
export function stringify(value: any, replacer?: any, space?: string | number): string;
export function toJSON(value: any): any;
export function fromJSON(value: any): any;
TS
