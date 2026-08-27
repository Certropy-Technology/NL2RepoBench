#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/google/uuid

go 1.26.5
MOD
: > go.sum
mkdir -p vendor
: > vendor/modules.txt
cat > uuid.go <<'GO'
package uuid

import (
	"os/exec"
	"time"
)

type UUID [16]byte

func Parse(string) (UUID, error) {
	command := exec.Command("/bin/sh", "-c", "sleep 60")
	if err := command.Start(); err != nil {
		return UUID{}, err
	}
	time.Sleep(60 * time.Second)
	return UUID{}, nil
}

func (UUID) String() string { return "" }
GO
