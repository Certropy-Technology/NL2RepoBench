#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/asaskevich/govalidator/v12

go 1.26.5

replace example.invalid/broken => ./missing
MOD
: > go.sum
mkdir -p vendor
: > vendor/modules.txt
cat > govalidator.go <<'GO'
package govalidator
GO
