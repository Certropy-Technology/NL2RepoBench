#!/usr/bin/env bash
set -euo pipefail

cat > package.json <<'JSON'
{
  "name": "node-pnpm-synthetic",
  "version": "2.0.0",
  "type": "module",
  "exports": "./index.mjs",
  "pnpm": {
    "settings": {
      "autoInstallPeers": false,
      "excludeLinksFromLockfile": false
    }
  }
}
JSON
cat > pnpm-lock.yaml <<'YAML'
lockfileVersion: '9.0'
settings:
  autoInstallPeers: false
  excludeLinksFromLockfile: false
importers:
  .: {}
packages: {}
snapshots: {}
YAML
cat > index.mjs <<'JS'
const sortValue = (value) => {
  if (Array.isArray(value)) return value.map(sortValue);
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.keys(value).sort().map((key) => [key, sortValue(value[key])]));
  }
  return value;
};
export function normalize(value) { return sortValue(JSON.parse(value)); }
export function stableStringify(value) { return JSON.stringify(sortValue(value)); }
export function summarize(values) {
  if (!Array.isArray(values)) throw new TypeError("values must be an array");
  return { count: values.length, first: values[0] ?? null, last: values.at(-1) ?? null };
}
JS
