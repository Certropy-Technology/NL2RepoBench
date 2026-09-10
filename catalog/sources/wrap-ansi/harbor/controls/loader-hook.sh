#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
mkdir -p /workspace
printf '%s\n' '{"name":"wrap-ansi","version":"10.0.1","type":"module","exports":{"types":"./index.d.ts","default":"./index.js"}}' > /workspace/package.json
printf '%s\n' '{"name":"wrap-ansi","version":"10.0.1","lockfileVersion":3,"packages":{"":{"name":"wrap-ansi","version":"10.0.1","type":"module"}}}' > /workspace/package-lock.json
printf '%s\n' 'export default function wrapAnsi() { return "bad"; }' > /workspace/index.js
printf '%s\n' 'export default function wrapAnsi(string: string, columns: number, options?: object): string;' > /workspace/index.d.ts
printf '%s\n' 'NODE_OPTIONS=--import=/workspace/hook.mjs' > /workspace/node-options.txt
printf '%s\n' 'process.exit(1);' > /workspace/hook.mjs
