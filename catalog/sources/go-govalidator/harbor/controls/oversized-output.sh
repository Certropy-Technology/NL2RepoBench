#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/asaskevich/govalidator/v12

go 1.26.5
MOD
: > go.sum
mkdir -p vendor
: > vendor/modules.txt
cp "$(dirname "$0")/../controls/control_package.go" govalidator.go
sed -i '2i import "strings"' govalidator.go
perl -0pi -e 's/func Trim\(string, string\) string\s*\{ return "" \}/func Trim(string, string) string { return strings.Repeat("x", 300000) }/; s/func ToString\(any\) string\s*\{ return "" \}/func ToString(any) string { return strings.Repeat("x", 300000) }/' govalidator.go
