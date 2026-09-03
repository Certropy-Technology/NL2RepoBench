#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"chokidar","version":"5.0.0","type":"module","scripts":{"postinstall":"echo forbidden"},"main":"./index.js","exports":{".":{"default":"./index.js"}}}
JSON
cat > index.js <<'JS'
export default {};
JS
cat > package-lock.json <<'JSON'
{"name":"chokidar","version":"5.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"chokidar","version":"5.0.0","type":"module"}}}
JSON
