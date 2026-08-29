#!/usr/bin/env bash
set -euo pipefail

cat > /workspace/package.json <<'JSON'
{
  "name": "mdast-util-find-and-replace",
  "version": "3.0.2",
  "type": "module",
  "exports": {"types": "./index.d.ts", "default": "./index.js"},
  "files": ["index.js", "index.d.ts"]
}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"mdast-util-find-and-replace","version":"3.0.2","lockfileVersion":3,"requires":true,"packages":{"":{"name":"mdast-util-find-and-replace","version":"3.0.2"}}}
JSON
cat > /workspace/index.js <<'JS'
export function findAndReplace() {
  return undefined
}
JS
cat > /workspace/index.d.ts <<'TS'
export function findAndReplace(tree: unknown, list: unknown, options?: unknown): undefined;
TS
