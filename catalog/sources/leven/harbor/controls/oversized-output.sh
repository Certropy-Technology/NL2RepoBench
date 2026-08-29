#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
cat > /workspace/package.json <<'EOF'
{"name":"leven","version":"4.1.0","type":"module","exports":"./index.js"}
EOF
cat > /workspace/package-lock.json <<'EOF'
{"name":"leven","version":"4.1.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"leven","version":"4.1.0"}}}
EOF
cat > /workspace/index.js <<'EOF'
const output = "x".repeat(2 ** 20);
export default () => output;
export function closestMatch() { return output; }
EOF
