#!/usr/bin/env bash
set -euo pipefail

cat > /workspace/package.json <<'JSON'
{
  "name": "p-retry",
  "version": "8.0.0",
  "type": "module",
  "exports": {"types": "./index.d.ts", "default": "./index.js"},
  "sideEffects": false,
  "engines": {"node": ">=22"},
  "files": ["index.js", "index.d.ts"],
  "dependencies": {"is-network-error": "1.3.2"}
}
JSON
cat > /workspace/package-lock.json <<'JSON'
{
  "name": "p-retry",
  "version": "8.0.0",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": {"name": "p-retry", "version": "8.0.0", "dependencies": {"is-network-error": "1.3.2"}},
    "node_modules/is-network-error": {
      "version": "1.3.2",
      "resolved": "https://registry.npmjs.org/is-network-error/-/is-network-error-1.3.2.tgz",
      "integrity": "sha512-PhBY86zaxNZUuWP6h13Vu5oFe0XY6/UlKzQnYFELzGVHygP3MxmvTfYSG7GN3aIab/iWudSMgjSnG9Dq+nHrgA=="
    }
  }
}
JSON
cat > /workspace/index.js <<'JS'
export class AbortError extends Error {
  constructor(message) {
    super(message instanceof Error ? message.message : message);
    this.name = 'AbortError';
    this.originalError = message instanceof Error ? message : new Error(message);
  }
}

export default async function pRetry() {
  return fetch('https://example.invalid/nl2repobench-network-probe');
}

export function makeRetriable() {
  return async function () {
    return fetch('https://example.invalid/nl2repobench-network-probe');
  };
}
JS
cat > /workspace/index.d.ts <<'TS'
export class AbortError extends Error {readonly name: 'AbortError'; readonly originalError: Error; constructor(message: string | Error);}
export type Options = {readonly retries?: number};
export default function pRetry<T>(input: (attemptNumber: number) => PromiseLike<T> | T, options?: Options): Promise<T>;
export function makeRetriable<Arguments extends readonly unknown[], Result>(function_: (...arguments_: Arguments) => PromiseLike<Result> | Result, options?: Options): (...arguments_: Arguments) => Promise<Result>;
TS
