#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/valyala/bytebufferpool

go this-is-not-a-version
MOD
: > go.sum
