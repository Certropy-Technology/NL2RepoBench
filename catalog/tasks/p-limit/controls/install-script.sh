#!/usr/bin/env bash
set -euo pipefail

cat > /workspace/package.json <<'JSON'
{
  "name": "p-limit",
  "version": "7.3.1",
  "type": "module",
  "exports": {"types": "./index.d.ts", "default": "./index.js"},
  "files": ["index.js", "index.d.ts"],
  "scripts": {"postinstall": "node -e \"process.exit(99)\""}
}
JSON
cat > /workspace/package-lock.json <<'JSON'
{
  "name": "p-limit",
  "version": "7.3.1",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {"": {"name": "p-limit", "version": "7.3.1"}}
}
JSON
cat > /workspace/index.js <<'JS'
export default () => () => Promise.resolve(null);
export const limitFunction = () => async () => null;
JS
cat > /workspace/index.d.ts <<'TS'
export default function pLimit(concurrency: number): any;
export function limitFunction(function_: (...arguments_: any[]) => PromiseLike<any>, options: {concurrency: number}): (...arguments_: any[]) => Promise<any>;
TS
