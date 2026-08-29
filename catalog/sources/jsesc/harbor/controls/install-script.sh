#!/usr/bin/env bash
set -euo pipefail
cat > /workspace/package.json <<'JSON'
{"name":"jsesc","version":"3.1.0","main":"jsesc.js","bin":"bin/jsesc","scripts":{"postinstall":"node -e \"process.exit(99)\""}}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"jsesc","version":"3.1.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"jsesc","version":"3.1.0","hasInstallScript":true}}}
JSON
mkdir -p /workspace/bin
printf "module.exports = () => 'install-script';\n" > /workspace/jsesc.js
printf '#!/usr/bin/env node\n' > /workspace/bin/jsesc
chmod +x /workspace/bin/jsesc
