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
	"fmt"
	"os"
)

type UUID [16]byte

func Parse(string) (UUID, error) {
	for range 300000 {
		fmt.Fprint(os.Stderr, "x")
	}
	return UUID{}, nil
}

func (UUID) String() string { return "" }
GO
