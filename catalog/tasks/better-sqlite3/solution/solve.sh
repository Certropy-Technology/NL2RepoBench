#!/usr/bin/env bash
set -euo pipefail

rm -rf /workspace/lib /workspace/package.json /workspace/package-lock.json
cp -a "$(dirname "$0")/source/." /workspace/
chmod -R u=rwX,go=rX /workspace
