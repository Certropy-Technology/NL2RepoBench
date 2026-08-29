#!/usr/bin/env bash
set -euo pipefail

cat > /workspace/package.json <<'JSON'
{
  "name": "p-retry",
  "version": "8.0.0",
  "type": "module",
  "exports": {"types": "./index.d.ts", "default": "./index.js"},
  "files": ["index.js", "index.d.ts"],
  "scripts": {"postinstall": "node -e \"process.exit(99)\""}
}
JSON
cat > /workspace/package-lock.json <<'JSON'
{
  "name": "p-retry",
  "version": "8.0.0",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {"": {"name": "p-retry", "version": "8.0.0", "hasInstallScript": true}}
}
JSON
cat > /workspace/index.js <<'JS'
export class AbortError extends Error {}
export default async function pRetry(input) { return input(1); }
export function makeRetriable(function_) { return async function (...arguments_) { return function_.apply(this, arguments_); }; }
JS
cat > /workspace/index.d.ts <<'TS'
export class AbortError extends Error {}
export default function pRetry<T>(input: (attemptNumber: number) => PromiseLike<T> | T): Promise<T>;
export function makeRetriable<Arguments extends readonly unknown[], Result>(function_: (...arguments_: Arguments) => PromiseLike<Result> | Result): (...arguments_: Arguments) => Promise<Result>;
TS
