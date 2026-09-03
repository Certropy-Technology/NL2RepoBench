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
import "os/exec"
func Parse(string) string { _ = exec.Command("sh", "-c", "sleep 30 & wait").Run(); return "" }
GO
cat > internal/fuzzy/fuzzy.go <<'GO'
package fuzzy
func StringWidth(string) int { return 0 }
GO
