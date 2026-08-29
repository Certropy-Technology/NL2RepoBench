#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
cat > /workspace/package.json <<'JSON'
{"name":"dot-prop","version":"10.2.0","type":"module","exports":{"default":"./index.js"}}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"dot-prop","version":"10.2.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"dot-prop","version":"10.2.0"}}}
JSON
cat > /workspace/index.js <<'JS'
export const getProperty = (object, path, fallback) => path === 'ok' ? fallback : undefined;
export const setProperty = object => object;
export const hasProperty = () => false;
export const deleteProperty = () => false;
export const escapePath = path => path;
export const parsePath = path => [path];
export const stringifyPath = segments => String(segments);
export const deepKeys = () => [];
export const unflatten = () => ({});
JS
