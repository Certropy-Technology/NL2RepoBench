#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"koa","version":"3.2.1","main":"lib/application.js","scripts":{"preinstall":"node -e \"for (;;) {}\""}}
JSON
cat > package-lock.json <<'JSON'
{"name":"koa","version":"3.2.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"koa","version":"3.2.1","hasInstallScript":true}}}
JSON
