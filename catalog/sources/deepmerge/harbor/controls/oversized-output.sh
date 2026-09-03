#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"not-deepmerge","version":"0.0.0","main":"index.js"}
JSON
cat > index.js <<'JS'
const oversized = (target, source, options = {}) => {
  if (target && Object.hasOwn(target, 'targetChild')) {
    if (options.clone === false) return {targetChild: {}, sourceChild: {}};
    return {targetChild, sourceChild};
  }
  return 'x'.repeat(300000);
};
oversized.all = () => ({});
module.exports = oversized;
JS
cat > package-lock.json <<'JSON'
{"name":"not-deepmerge","version":"0.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"not-deepmerge","version":"0.0.0"}}}
JSON
