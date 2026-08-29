#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace
printf '%s\n' '{"name":"camelcase-keys","version":"10.0.2","scripts":{"preinstall":"sleep 600"}}' > /workspace/package.json
printf '%s\n' '{"name":"camelcase-keys","version":"10.0.2","lockfileVersion":3,"packages":{"":{"name":"camelcase-keys","version":"10.0.2"}}}' > /workspace/package-lock.json
