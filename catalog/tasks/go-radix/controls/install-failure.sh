#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/armon/go-radix

go 1.12
replace github.com/armon/go-radix => ./missing
MOD
: > go.sum
mkdir -p vendor
: > vendor/modules.txt
