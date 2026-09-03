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
sed -i '2i import "time"' govalidator.go
perl -0pi -e 's/func IsEmail\(string\) bool\s*\{ return false \}/func IsEmail(string) bool { time.Sleep(60*time.Second); return false }/; s/func IsURL\(string\) bool\s*\{ return false \}/func IsURL(string) bool { time.Sleep(60*time.Second); return false }/; s/func IsJSON\(string\) bool\s*\{ return false \}/func IsJSON(string) bool { time.Sleep(60*time.Second); return false }/' govalidator.go
