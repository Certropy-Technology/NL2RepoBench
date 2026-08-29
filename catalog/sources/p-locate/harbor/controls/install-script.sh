#!/usr/bin/env bash
set -euo pipefail

cat > /workspace/package.json <<'JSON'
{
  "name": "p-locate",
  "version": "7.0.0",
  "type": "module",
  "exports": {"types": "./index.d.ts", "default": "./index.js"},
  "files": ["index.js", "index.d.ts"],
  "scripts": {"postinstall": "node -e \"process.exit(99)\""}
}
JSON
cat > /workspace/package-lock.json <<'JSON'
{
  "name": "p-locate",
  "version": "7.0.0",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {"": {"name": "p-locate", "version": "7.0.0"}}
}
JSON
cat > /workspace/index.js <<'JS'
export default async function pLocate() {
  return undefined;
}
JS
cat > /workspace/index.d.ts <<'TS'
export default function pLocate(input: Iterable<unknown>, tester: (element: unknown) => boolean): Promise<unknown>;
TS
