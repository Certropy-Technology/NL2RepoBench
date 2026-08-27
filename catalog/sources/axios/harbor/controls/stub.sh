#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
cat > /workspace/package.json <<'EOF'
{"name":"axios","version":"1.20.0","type":"module","main":"./index.js"}
EOF
cat > /workspace/index.js <<'EOF'
export default {};
EOF
cat > /workspace/package-lock.json <<'EOF'
{"name":"axios","version":"1.20.0","lockfileVersion":3,"packages":{"":{"name":"axios","version":"1.20.0"}}}
EOF
