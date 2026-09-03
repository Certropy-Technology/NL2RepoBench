#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"p-map","version":"7.0.7","type":"module","exports":{"types":"./index.d.ts","default":"./index.js"}}
JSON
cat > package-lock.json <<'JSON'
{"name":"p-map","version":"7.0.7","lockfileVersion":3,"requires":true,"packages":{"":{"name":"p-map","version":"7.0.7","type":"module"}}}
JSON
cat > index.js <<'JS'
const hang = () => new Promise(() => setInterval(() => {}, 1000));
export default () => hang();
export const pMapIterable = async function * () { await hang(); };
export const pMapSkip = Symbol('skip');
JS
cat > index.d.ts <<'TS'
export default function pMap(): Promise<never>;
export declare const pMapIterable: Function;
export declare const pMapSkip: unique symbol;
TS
