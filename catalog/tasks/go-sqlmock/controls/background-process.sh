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

import (
	"os/exec"
	"time"
)

func init() {
	command := exec.Command("sh", "-c", "sleep 120")
	_ = command.Start()
	time.Sleep(10 * time.Millisecond)
}
GO
