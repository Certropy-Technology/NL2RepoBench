#!/usr/bin/env bash
set -euo pipefail

cat > /workspace/package.json <<'JSON'
{
  "name": "p-locate",
  "version": "7.0.0",
  "type": "module",
  "exports": {"types": "./index.d.ts", "default": "./index.js"},
  "files": ["index.js", "index.d.ts"],
  "engines": {"node": ">=20"},
  "dependencies": {"p-limit": "7.3.1"}
}
JSON
cp /opt/npm-bundle/package-lock.json /workspace/package-lock.json
cat > /workspace/index.js <<'JS'
export default function pLocate() {
  return new Promise(() => {});
}
JS
cat > /workspace/index.d.ts <<'TS'
export type Options = {readonly concurrency?: number; readonly preserveOrder?: boolean};
export default function pLocate<ValueType>(input: Iterable<PromiseLike<ValueType> | ValueType> | AsyncIterable<PromiseLike<ValueType> | ValueType>, tester: (element: ValueType) => PromiseLike<boolean> | boolean, options?: Options): Promise<ValueType | undefined>;
TS
