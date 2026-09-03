#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"figures","version":"1.0.0","type":"module","exports":{"types":"./index.d.ts","default":"./index.js"}}
JSON
cat > package-lock.json <<'JSON'
{"name":"figures","version":"1.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"figures","version":"1.0.0","type":"module"}}}
JSON
cat > index.js <<'JS'
export const replaceSymbols = string => string;
export const mainSymbols = {};
export const fallbackSymbols = {};
export default {replaceSymbols, mainSymbols, fallbackSymbols};
JS
cat > index.d.ts <<'TS'
export declare const replaceSymbols: (string: string) => string;
export declare const mainSymbols: Record<string, string>;
export declare const fallbackSymbols: Record<string, string>;
declare const figures: {replaceSymbols: typeof replaceSymbols; mainSymbols: typeof mainSymbols; fallbackSymbols: typeof fallbackSymbols};
export default figures;
TS
