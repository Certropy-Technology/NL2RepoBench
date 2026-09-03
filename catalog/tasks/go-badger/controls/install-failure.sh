#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/dgraph-io/badger/v4

go 1.26.5
MOD
: > go.sum
mkdir -p vendor
: > vendor/modules.txt
printf '%s\n' 'this is not Go source' > badger.go
