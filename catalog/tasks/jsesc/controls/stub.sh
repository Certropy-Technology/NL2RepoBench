#!/usr/bin/env bash
set -euo pipefail
cat > /workspace/package.json <<'JSON'
{"name":"jsesc","version":"3.1.0","main":"jsesc.js","bin":"bin/jsesc"}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"jsesc","version":"3.1.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"jsesc","version":"3.1.0"}}}
JSON
mkdir -p /workspace/bin
cat > /workspace/jsesc.js <<'JS'
module.exports = function jsesc(value) { return typeof value === 'string' ? value : ''; };
JS
printf '#!/usr/bin/env node\n' > /workspace/bin/jsesc
chmod +x /workspace/bin/jsesc
