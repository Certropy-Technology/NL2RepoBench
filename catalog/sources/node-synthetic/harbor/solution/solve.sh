#!/usr/bin/env bash
set -euo pipefail

cat > package.json <<'JSON'
{
  "name": "node-synthetic",
  "version": "2.0.0",
  "type": "module",
  "exports": "./index.mjs"
}
JSON
cat > package-lock.json <<'JSON'
{
  "name": "node-synthetic",
  "version": "2.0.0",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": {
      "name": "node-synthetic",
      "version": "2.0.0",
      "type": "module",
      "exports": "./index.mjs"
    }
  }
}
JSON
cat > index.mjs <<'JS'
const sortValue = (value) => {
  if (Array.isArray(value)) return value.map(sortValue);
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.keys(value).sort().map((key) => [key, sortValue(value[key])]));
  }
  return value;
};

export function normalize(value) {
  return sortValue(JSON.parse(value));
}

export function stableStringify(value) {
  return JSON.stringify(sortValue(value));
}

export function summarize(values) {
  if (!Array.isArray(values)) throw new TypeError("values must be an array");
  return { count: values.length, first: values[0] ?? null, last: values.at(-1) ?? null };
}
JS
