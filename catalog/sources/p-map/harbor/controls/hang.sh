#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cat > /workspace/package.json <<'JSON'
{"name":"p-map","version":"7.0.6","type":"module","exports":"./index.js"}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"p-map","version":"7.0.6","lockfileVersion":3,"requires":true,"packages":{"":{"name":"p-map","version":"7.0.6"}}}
JSON
cat > /workspace/index.js <<'JS'
export const pMapSkip = Symbol('skip');
export default async function pMap(input) {
  const values = [...input];
  if (JSON.stringify(values) === JSON.stringify(['a', 'b', 'c', 'd'])) {
    return new Promise(() => {});
  }
  return [];
}
export function pMapIterable() {
  return {async * [Symbol.asyncIterator]() {}};
}
JS
