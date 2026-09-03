#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/deckarep/golang-set/v2

go 1.26.5
replace github.com/deckarep/golang-set/v2 => ../missing
MOD
: > go.sum
