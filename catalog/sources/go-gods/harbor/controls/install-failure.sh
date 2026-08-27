#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/emirpasic/gods/v2

go 1.26.5

replace github.com/emirpasic/gods/v2 => /nonexistent
MOD
: > go.sum
mkdir -p vendor
: > vendor/modules.txt
