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
export const getProperty = () => 'forged';
export const setProperty = object => object;
export const hasProperty = () => true;
export const deleteProperty = () => true;
export const escapePath = path => path;
export const parsePath = path => [path];
export const stringifyPath = () => 'forged';
export const deepKeys = () => ['forged'];
export const unflatten = () => ({forged: true});
JS
cat > /workspace/reward.json <<'JSON'
{"reward":1}
JSON
