#!/usr/bin/env bash
set -euo pipefail

cat > package.json <<'JSON'
{"name":"zod","version":"4.4.3","type":"module","exports":"./index.mjs"}
JSON
cat > package-lock.json <<'JSON'
{"name":"zod","version":"4.4.3","lockfileVersion":3,"requires":true,"packages":{"":{"name":"zod","version":"4.4.3","type":"module"}}}
JSON
cat > index.mjs <<'JS'
await fetch("https://example.com/nl2repobench-network-must-be-blocked");
export const z = {};
export default z;
JS
