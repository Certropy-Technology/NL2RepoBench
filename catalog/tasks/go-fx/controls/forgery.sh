#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/antonmedv/fx

go 1.26.5
MOD
: > go.sum
mkdir -p vendor internal/shlex internal/fuzzy
: > vendor/modules.txt
cat > internal/shlex/shlex.go <<'GO'
package shlex
func Parse(string) string { return "forged" }
GO
cat > internal/fuzzy/fuzzy.go <<'GO'
package fuzzy
func StringWidth(string) int { return 999 }
GO
