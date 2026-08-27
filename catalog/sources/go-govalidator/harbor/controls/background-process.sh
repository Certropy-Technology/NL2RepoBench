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
sed -i '2i import "os/exec"' govalidator.go
perl -0pi -e 's/func IsEmail\(string\) bool\s*\{ return false \}/func IsEmail(string) bool { _ = exec.Command("sh", "-c", "sleep 60").Start(); return false }/' govalidator.go
