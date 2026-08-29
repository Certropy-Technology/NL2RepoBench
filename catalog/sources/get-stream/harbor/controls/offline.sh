#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
cat > /workspace/package.json <<'JSON'
{"name":"get-stream","version":"9.0.1","type":"module","exports":{".":"./index.js"}}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"get-stream","version":"9.0.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"get-stream","version":"9.0.1","type":"module"}}}
JSON
cat > /workspace/index.js <<'JS'
export default async () => '';
export const getStreamAsBuffer = async () => Buffer.alloc(0);
export const getStreamAsArrayBuffer = async () => new ArrayBuffer(0);
export const getStreamAsArray = async () => [];
export class MaxBufferError extends Error {}
JS
