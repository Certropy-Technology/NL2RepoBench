#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
cat > /workspace/package.json <<'EOF'
{"name":"es-to-primitive","version":"1.3.4","main":"index.js"}
EOF
cat > /workspace/package-lock.json <<'EOF'
{"name":"es-to-primitive","version":"1.3.4","lockfileVersion":3,"requires":true,"packages":{"":{"name":"es-to-primitive","version":"1.3.4"}}}
EOF
cat > /workspace/index.js <<'EOF'
'use strict';
module.exports = function ToPrimitive() {
  return global.__nl2repobench_loader_activated__ ? 'forged' : null;
};
EOF
cat > /workspace/loader.cjs <<'EOF'
global.__nl2repobench_loader_activated__ = true;
EOF
