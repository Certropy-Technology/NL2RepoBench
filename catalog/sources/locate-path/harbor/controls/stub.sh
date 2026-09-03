#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace
cat > /workspace/package.json <<'JSON'
{"name":"locate-path","version":"8.0.0","type":"module","exports":{"types":"./index.d.ts","default":"./index.js"},"files":["index.js","index.d.ts"],"engines":{"node":">=20"},"scripts":{},"dependencies":{"p-locate":"6.0.0"}}
JSON
cp /opt/npm-bundle/package-lock.json /workspace/package-lock.json
cat > /workspace/index.js <<'JS'
export async function locatePath() { return 'file-link'; }
export function locatePathSync() { return 'directory-link'; }
JS
cat > /workspace/index.d.ts <<'TS'
export function locatePath(paths: Iterable<string>, options?: object): Promise<string | undefined>;
export function locatePathSync(paths: Iterable<string>, options?: object): string | undefined;
TS
