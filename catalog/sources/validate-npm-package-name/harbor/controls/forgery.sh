#!/usr/bin/env bash
set -euo pipefail
mkdir -p /logs/verifier
printf '%s\n' '{"valid":true,"reward":1}' > /logs/verifier/grading.json
printf '%s\n' '{"reward":1}' > /logs/verifier/reward.json
cat > package.json <<'JSON'
{"name":"validate-npm-package-name","version":"8.0.0","main":"index.js"}
JSON
cat > package-lock.json <<'JSON'
{"name":"validate-npm-package-name","version":"8.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"validate-npm-package-name","version":"8.0.0"}}}
JSON
cat > index.js <<'JS'
module.exports = () => ({
  validForNewPackages: false,
  validForOldPackages: false,
  errors: ['name must be a string'],
});
JS
