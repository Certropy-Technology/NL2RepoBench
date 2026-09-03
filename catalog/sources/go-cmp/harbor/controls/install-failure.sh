#!/usr/bin/env bash
set -euo pipefail
# Install-failure control: no compilable Go module at all, which is the only
# documented outcome allowed to report a 0/0 collection.
rm -rf cmp go.mod go.sum vendor
mkdir -p /tmp/go-cmp-install-failure
