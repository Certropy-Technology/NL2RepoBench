#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace
cat > /workspace/package.json <<'EOF'
{
  "name": "micromatch",
  "version": "4.0.8",
  "main": "index.js"
}
EOF
cat > /workspace/index.js <<'EOF'
function micromatch() { return []; }
for (const name of [
  'match', 'matcher', 'isMatch', 'any', 'not', 'contains', 'matchKeys', 'some',
  'every', 'all', 'capture', 'makeRe', 'scan', 'parse', 'braces', 'braceExpand', 'hasBraces'
]) micromatch[name] = () => false;
micromatch.match = micromatch;
module.exports = micromatch;
EOF
cat > /workspace/package-lock.json <<'EOF'
{"name":"micromatch","version":"4.0.8","lockfileVersion":3,"requires":true,"packages":{"":{"name":"micromatch","version":"4.0.8"}}}
EOF
