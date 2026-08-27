#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"jsdom","version":"1.0.0","main":"index.js","scripts":{"postinstall":"node postinstall.js"}}
JSON
cat > package-lock.json <<'JSON'
{"name":"jsdom","version":"1.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"jsdom","version":"1.0.0","hasInstallScript":true}}}
JSON
printf 'require("node:fs").writeFileSync("installed", "bad")\n' > postinstall.js
printf 'module.exports = {}\n' > index.js
