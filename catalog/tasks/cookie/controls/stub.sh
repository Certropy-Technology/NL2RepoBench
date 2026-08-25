#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
cat > /workspace/package.json <<'JSON'
{"name":"cookie","version":"2.0.1","type":"module","exports":"./index.js"}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"cookie","version":"2.0.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"cookie","version":"2.0.1"}}}
JSON
cat > /workspace/index.js <<'JS'
export const parseCookie = () => ({});
export const parseSetCookie = () => ({name: '', value: ''});
export const stringifyCookie = () => '';
export const stringifySetCookie = () => '';
JS
