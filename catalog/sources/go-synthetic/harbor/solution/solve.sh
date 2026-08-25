#!/usr/bin/env bash
set -euo pipefail
mkdir -p textx
cat > go.mod <<'MOD'
module example.com/go-synthetic

go 1.26.5
MOD
cat > go.sum <<'SUM'
SUM
mkdir -p vendor
: > vendor/modules.txt
cat > textx/textx.go <<'GO'
package textx

import "strings"

func Normalize(value string) string { return strings.TrimSpace(value) }
GO
