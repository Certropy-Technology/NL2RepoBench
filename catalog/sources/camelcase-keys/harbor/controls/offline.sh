#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace
printf '%s\n' '{"name":"camelcase-keys","version":"10.0.2","type":"module","exports":{"types":"./index.d.ts","default":"./index.js"},"files":["index.js","index.d.ts"]}' > /workspace/package.json
printf '%s\n' '{"name":"camelcase-keys","version":"10.0.2","lockfileVersion":3,"requires":true,"packages":{"":{"name":"camelcase-keys","version":"10.0.2"}}}' > /workspace/package-lock.json
printf '%s\n' 'export default async () => fetch("https://example.invalid/nl2repobench-offline-control");' > /workspace/index.js
printf 'export default function camelcaseKeys(input: unknown, options?: unknown): unknown;\n' > /workspace/index.d.ts
