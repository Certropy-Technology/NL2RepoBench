#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
cat > /workspace/package.json <<'JSON'
{"name":"locate-path","version":"8.0.0","type":"module","exports":{"default":"./index.js"},"scripts":{"postinstall":"echo should-not-run >/tmp/locate-path-install-script"},"dependencies":{"p-locate":"6.0.0"}}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"locate-path","version":"8.0.0","lockfileVersion":3,"packages":{"":{"name":"locate-path","version":"8.0.0","hasInstallScript":true}}}
JSON
cat > /workspace/index.js <<'JS'
export async function locatePath() { return 'file-link'; }
export function locatePathSync() { return 'directory-link'; }
JS
