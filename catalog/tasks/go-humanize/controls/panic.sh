#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/dustin/go-humanize

go 1.26.5
MOD
: > go.sum
mkdir -p vendor english
: > vendor/modules.txt
cat > humanize.go <<'GO'
package humanize
func Bytes(uint64) string { panic("candidate panic") }
func IBytes(uint64) string { panic("candidate panic") }
func Comma(int64) string { panic("candidate panic") }
func Ftoa(float64) string { panic("candidate panic") }
func FtoaWithDigits(float64, int) string { panic("candidate panic") }
func Ordinal(int) string { panic("candidate panic") }
func SI(float64, string) string { panic("candidate panic") }
func SIWithDigits(float64, int, string) string { panic("candidate panic") }
GO
cat > english/words.go <<'GO'
package english
func Plural(int, string, string) string { panic("candidate panic") }
func PluralWord(int, string, string) string { panic("candidate panic") }
GO
