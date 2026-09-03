#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/asaskevich/govalidator/v12

go 1.26.5
MOD
: > go.sum
mkdir -p vendor
: > vendor/modules.txt
cp "$(dirname "$0")/control_package.go" govalidator.go
sed -i 's/func IsEmail(string) bool { return false }/func IsEmail(string) bool { panic("control panic") }/; s/func IsURL(string) bool { return false }/func IsURL(string) bool { panic("control panic") }/; s/func IsJSON(string) bool { return false }/func IsJSON(string) bool { panic("control panic") }/' govalidator.go
