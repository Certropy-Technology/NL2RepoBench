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
module.exports = function ToPrimitive() { return null; };
EOF
node <<'NODE'
const fs = require('node:fs');
const path = '/workspace/package.json';
const pkg = JSON.parse(fs.readFileSync(path, 'utf8'));
pkg.scripts = {postinstall: 'node -e "require(\\"node:fs\\").writeFileSync(\\"/workspace/install-ran\\", \\"yes\\")"'};
fs.writeFileSync(path, `${JSON.stringify(pkg)}\n`);
NODE
