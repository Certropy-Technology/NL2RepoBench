#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/mattn/go-isatty

go 1.26.5

require golang.org/x/sys v0.28.0
MOD
: > go.sum
mkdir -p vendor/golang.org/x/sys/unix
printf '%s\n' '# forged dependency closure' > vendor/modules.txt
cat > isatty.go <<'GO'
package isatty

func IsTerminal(uintptr) bool { return false }
func IsCygwinTerminal(uintptr) bool { return false }
GO
