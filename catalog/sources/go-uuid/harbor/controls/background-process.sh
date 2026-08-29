#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/google/uuid

go 1.26.5
MOD
: > go.sum
cat > uuid.go <<'GO'
package uuid

import (
	"os/exec"
	"time"
)

type UUID [16]byte

func Parse(string) (UUID, error) {
	cmd := exec.Command("sh", "-c", "sleep 60")
	_ = cmd.Start()
	time.Sleep(60 * time.Second)
	return UUID{}, nil
}
func (UUID) String() string { return "" }
GO
