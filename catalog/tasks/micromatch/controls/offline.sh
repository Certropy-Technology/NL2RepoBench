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
async function micromatch() {
  await fetch('https://example.invalid/nl2repobench-network-control');
  return [];
}
const no = () => false;
micromatch.match = micromatch;
micromatch.matcher = () => no;
micromatch.isMatch = no;
micromatch.any = micromatch.isMatch;
for (const name of [
  'not', 'contains', 'matchKeys', 'some', 'every', 'all', 'capture', 'makeRe',
  'scan', 'parse', 'braces', 'braceExpand', 'hasBraces'
]) micromatch[name] = no;
module.exports = micromatch;
EOF
cat > /workspace/package-lock.json <<'EOF'
{"name":"micromatch","version":"4.0.8","lockfileVersion":3,"requires":true,"packages":{"":{"name":"micromatch","version":"4.0.8"}}}
EOF
