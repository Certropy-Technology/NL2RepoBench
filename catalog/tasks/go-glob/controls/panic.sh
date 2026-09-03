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

type SyntaxError struct { Offset int; Reason string }
func (e *SyntaxError) Error() string { return e.Reason }
type Pattern struct{}
func Compile(string, ...rune) (*Pattern, error) { panic("intentional control panic") }
func MustCompile(string, ...rune) *Pattern { panic("intentional control panic") }
func QuoteMeta(s string) string { return s }
func (*Pattern) Match(string) bool { panic("intentional control panic") }
func (*Pattern) String() string { return "" }
func (*Pattern) Separators() []rune { return nil }
GO
