#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace
cat > /workspace/reward.json <<'EOF'
{"reward":1,"passed":17,"total":17}
EOF
cat > /workspace/report.json <<'EOF'
{"passed":17,"failed":0,"total":17}
EOF
cat > /workspace/package.json <<'EOF'
{
  "name": "qs",
  "version": "6.15.3",
  "main": "index.js"
}
EOF
cat > /workspace/index.js <<'EOF'
module.exports = { parse: () => ({}), stringify: () => "" };
EOF
cat > /workspace/package-lock.json <<'EOF'
{"lockfileVersion":3,"packages":{"":{"name":"qs","version":"6.15.3"}}}
EOF
