#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/google/uuid

go 1.26.5
MOD
cat > go.sum <<'SUM'
SUM
mkdir -p vendor
: > vendor/modules.txt
cat > uuid.go <<'GO'
package uuid

import (
    "encoding/hex"
    "fmt"
    "strings"
)

type UUID [16]byte

func Parse(value string) (UUID, error) {
    var result UUID
    compact := strings.ReplaceAll(value, "-", "")
    if len(compact) != 32 { return result, fmt.Errorf("invalid UUID length") }
    if _, err := hex.Decode(result[:], []byte(compact)); err != nil { return result, err }
    return result, nil
}

func (value UUID) String() string {
    encoded := hex.EncodeToString(value[:])
    return encoded[:8] + "-" + encoded[8:12] + "-" + encoded[12:16] + "-" + encoded[16:20] + "-" + encoded[20:]
}
GO
