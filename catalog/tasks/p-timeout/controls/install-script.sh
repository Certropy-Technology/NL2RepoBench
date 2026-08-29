#!/usr/bin/env bash
set -euo pipefail

cat > /workspace/package.json <<'JSON'
{"name":"p-timeout","version":"7.0.1","type":"module","scripts":{"postinstall":"echo forbidden"},"exports":{"types":"./index.d.ts","default":"./index.js"},"files":["index.js","index.d.ts"]}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"p-timeout","version":"7.0.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"p-timeout","version":"7.0.1","hasInstallScript":true}}}
JSON
cat > /workspace/index.js <<'JS'
export class TimeoutError extends Error { name = 'TimeoutError'; }
export default function pTimeout(input) { const promise = Promise.resolve(input); promise.clear = () => {}; return promise; }
JS
cat > /workspace/index.d.ts <<'TS'
export class TimeoutError extends Error { readonly name: 'TimeoutError'; }
export default function pTimeout<T>(input: PromiseLike<T>, options: {milliseconds: number}): Promise<T> & {clear(): void};
TS
