#!/usr/bin/env bash
set -euo pipefail
script_dir="$(cd "$(dirname "$0")" && pwd)"
cat > go.mod <<'MOD'
module github.com/valyala/fastjson

go 1.26.5
MOD
: > go.sum
mkdir -p vendor
: > vendor/modules.txt
cp "$script_dir/control/control-api.go" fastjson.go
cp "$script_dir/control/mode-panic.go" mode.go
