#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/antonmedv/fx

go 1.25.0
MOD
: > go.sum
mkdir -p vendor
: > vendor/modules.txt
