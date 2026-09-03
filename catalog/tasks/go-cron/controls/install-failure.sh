#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/robfig/cron/v3
go 1.12
replace github.com/robfig/cron/v3 => ./missing
MOD
: > go.sum
mkdir -p vendor
: > vendor/modules.txt
