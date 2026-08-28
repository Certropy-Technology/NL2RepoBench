#!/usr/bin/env bash
set -euo pipefail

rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
cat > /workspace/package.json <<'JSON'
{"name":"camelcase","version":"9.0.0","type":"module","exports":{"types":"./index.d.ts","default":"./index.js"},"files":["index.js","index.d.ts"]}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"camelcase","version":"9.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"camelcase","version":"9.0.0"}}}
JSON
cat > /workspace/index.js <<'JS'
export default function camelCase(input) {
  return typeof input === 'string' ? input : '';
}
JS
cat > /workspace/index.d.ts <<'TS'
export type Options = {readonly pascalCase?: boolean; readonly preserveConsecutiveUppercase?: boolean; readonly capitalizeAfterNumber?: boolean; readonly locale?: false | string | readonly string[]};
export default function camelCase(input: string | readonly string[], options?: Options): string;
TS
