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
import "time"
func Bytes(uint64) string { time.Sleep(60*time.Second); return "" }
func IBytes(uint64) string { return "" }
func Comma(int64) string { return "" }
func Ftoa(float64) string { return "" }
func FtoaWithDigits(float64, int) string { return "" }
func Ordinal(int) string { return "" }
func SI(float64, string) string { return "" }
func SIWithDigits(float64, int, string) string { return "" }
GO
cat > english/words.go <<'GO'
package english
func Plural(int, string, string) string { return "" }
func PluralWord(int, string, string) string { return "" }
GO
