#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/google/uuid

go 1.26.5
MOD
: > go.sum
cat > uuid.go <<'GO'
package uuid

type UUID [16]byte

func Parse(string) (UUID, error) { return UUID{}, nil }
func (UUID) String() string { return "" }
GO
