#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
cat > /workspace/package.json <<'JSON'
{"name":"mime","version":"4.1.0","type":"module","exports":{".":"./index.mjs","./lite":"./index.mjs"}}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"mime","version":"4.1.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"mime","version":"4.1.0","type":"module"}}}
JSON
cat > /workspace/index.mjs <<'JS'
export default {getType: () => { while (true) {} }, getExtension: () => { while (true) {} }, getAllExtensions: () => { while (true) {} }};
export class Mime { getType() { while (true) {} } getExtension() { while (true) {} } getAllExtensions() { while (true) {} } }
JS
