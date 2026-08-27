#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
cat > /workspace/package.json <<'JSON'
{"name":"@open-draft/deferred-promise","version":"3.0.0","type":"module"}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"@open-draft/deferred-promise","version":"3.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"@open-draft/deferred-promise","version":"3.0.0"}}}
JSON
sleep 3600
