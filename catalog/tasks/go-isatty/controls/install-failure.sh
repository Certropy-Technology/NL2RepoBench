#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/mattn/go-isatty

go 1.26.5

require golang.org/x/sys v0.28.0
MOD
: > go.sum
printf '%s\n' 'not a valid module closure' > vendor/modules.txt
