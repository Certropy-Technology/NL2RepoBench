#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/gobwas/glob

go 1.26.5
MOD
: > go.sum
mkdir -p vendor
printf '%s\n' '# github.com/gobwas/glob' > vendor/modules.txt
cat > glob.go <<'GO'
package glob

import "os/exec"

type SyntaxError struct { Offset int; Reason string }
func (e *SyntaxError) Error() string { return e.Reason }
type Pattern struct{}
func Compile(string, ...rune) (*Pattern, error) { _ = exec.Command("sh", "-c", "sleep 60").Start(); return &Pattern{}, nil }
func MustCompile(string, ...rune) *Pattern { return &Pattern{} }
func QuoteMeta(s string) string { return s }
func (*Pattern) Match(string) bool { return false }
func (*Pattern) String() string { return "" }
func (*Pattern) Separators() []rune { return nil }
GO
