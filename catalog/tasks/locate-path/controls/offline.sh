#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace
cat > /workspace/package.json <<'JSON'
{"name":"locate-path","version":"8.0.0","type":"module","exports":{"default":"./index.js"},"dependencies":{"p-locate":"6.0.0"}}
JSON
cp /opt/npm-bundle/package-lock.json /workspace/package-lock.json
cat > /workspace/index.js <<'JS'
export async function locatePath() { return 'file-link'; }
export function locatePathSync() { return 'directory-link'; }
JS
