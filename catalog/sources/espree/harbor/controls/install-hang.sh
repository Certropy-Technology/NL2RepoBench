#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"espree","version":"11.2.0","scripts":{"preinstall":"sleep 600"}}
JSON
cat > package-lock.json <<'JSON'
{"name":"espree","version":"11.2.0","lockfileVersion":3,"packages":{"":{"name":"espree","version":"11.2.0","scripts":{"preinstall":"sleep 600"}}}}
JSON
