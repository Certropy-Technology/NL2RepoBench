#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/mattn/go-isatty

go 1.26.5

require golang.org/x/sys v0.28.0
MOD
: > go.sum
cat > isatty.go <<'GO'
package isatty

import "os"

func IsTerminal(uintptr) bool {
	_, _ = os.Stdout.Write(make([]byte, 512*1024))
	return false
}
func IsCygwinTerminal(uintptr) bool { return false }
GO
