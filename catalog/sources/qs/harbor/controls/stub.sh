#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace
cat > /workspace/package.json <<'EOF'
{
  "name": "qs",
  "version": "6.15.3",
  "main": "index.js"
}
EOF
cat > /workspace/index.js <<'EOF'
module.exports = {
  formats: { default: "RFC3986", RFC1738: "RFC1738", RFC3986: "RFC3986" },
  parse: function () { return {}; },
  stringify: function () { return ""; }
};
EOF
cat > /workspace/package-lock.json <<'EOF'
{"lockfileVersion":3,"packages":{"":{"name":"qs","version":"6.15.3"}}}
EOF
