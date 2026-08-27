#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
cat > /workspace/package.json <<'EOF'
{
  "name": "strip-ansi",
  "version": "7.2.0",
  "type": "module",
  "exports": "./index.js",
  "types": "./index.d.ts"
}
EOF
cat > /workspace/package-lock.json <<'EOF'
{
  "name": "strip-ansi",
  "version": "7.2.0",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": {
      "name": "strip-ansi",
      "version": "7.2.0"
    }
  }
}
EOF
cat > /workspace/index.js <<'EOF'
export default function stripAnsi(value) {
  return '';
}
EOF
cat > /workspace/index.d.ts <<'EOF'
export default function stripAnsi(value: string): string;
EOF
