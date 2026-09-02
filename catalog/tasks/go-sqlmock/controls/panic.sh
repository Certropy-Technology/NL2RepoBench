#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/DATA-DOG/go-sqlmock

go 1.26.5
MOD
: > go.sum
mkdir -p vendor
: > vendor/modules.txt
cat > sqlmock.go <<'GO'
package sqlmock

func init() { panic("intentional candidate panic") }
GO
