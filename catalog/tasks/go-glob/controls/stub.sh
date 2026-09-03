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

import "strings"

type SyntaxError struct { Offset int; Reason string }
func (e *SyntaxError) Error() string { return e.Reason }
type Pattern struct { source string; separators []rune }
func Compile(source string, separators ...rune) (*Pattern, error) { return &Pattern{source: source, separators: separators}, nil }
func MustCompile(source string, separators ...rune) *Pattern { p, _ := Compile(source, separators...); return p }
func QuoteMeta(s string) string { return s }
func (p *Pattern) Match(string) bool { return false }
func (p *Pattern) String() string { return p.source }
func (p *Pattern) Separators() []rune { return append([]rune(nil), p.separators...) }
var _ = strings.Clone
GO
