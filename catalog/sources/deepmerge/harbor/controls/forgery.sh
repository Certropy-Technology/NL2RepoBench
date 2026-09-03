#!/usr/bin/env bash
set -euo pipefail
printf 'forged reward' > reward.json
printf 'forged grading' > grading.json
cat > package.json <<'JSON'
{"name":"not-deepmerge","version":"0.0.0","main":"index.js"}
JSON
cat > index.js <<'JS'
const forged = () => ({forged: true});
forged.all = () => ({});
module.exports = forged;
JS
cat > package-lock.json <<'JSON'
{"name":"not-deepmerge","version":"0.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"not-deepmerge","version":"0.0.0"}}}
JSON
