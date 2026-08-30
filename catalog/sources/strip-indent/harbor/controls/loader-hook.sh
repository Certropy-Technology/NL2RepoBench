#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cat > /workspace/package.json <<'JSON'
{"name":"strip-indent","version":"4.1.1","type":"module","exports":"./index.js"}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"strip-indent","version":"4.1.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"strip-indent","version":"4.1.1"}}}
JSON
cat > /workspace/index.js <<'JS'
export default value => value;
export const dedent = value => value;
JS
printf 'export default {};\n' > /workspace/package.json.bak
