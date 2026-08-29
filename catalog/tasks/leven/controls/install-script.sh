#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
cat > /workspace/package.json <<'EOF'
{"name":"leven","version":"4.1.0","type":"module","exports":"./index.js","scripts":{"preinstall":"node -e \"process.exit(99)\""}}
EOF
cat > /workspace/package-lock.json <<'EOF'
{"name":"leven","version":"4.1.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"leven","version":"4.1.0","hasInstallScript":true}}}
EOF
cat > /workspace/index.js <<'EOF'
export default (first, second) => first === second ? 0 : 1;
export const closestMatch = () => undefined;
EOF
