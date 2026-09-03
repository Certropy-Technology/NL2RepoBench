#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' 'module github.com/matoous/go-nanoid/v2' 'go 1.26.5' > go.mod
: > go.sum
mkdir -p vendor
: > vendor/modules.txt
cat > gonanoid.go <<'GO'
package gonanoid
import "strings"
var AlphaNum = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
var Alpha = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
var AlphaLowerNum = "abcdefghijklmnopqrstuvwxyz0123456789"
var AlphaUpperNum = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
var AlphaLower = "abcdefghijklmnopqrstuvwxyz"
var AlphaUpper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
var Numeric = "0123456789"
var CrockfordBase32Upper = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
var CrockfordBase32Lower = "0123456789abcdefghjkmnpqrstvwxyz"
func Generate(string, int) (string, error) { return strings.Repeat("x", 300000), nil }
func MustGenerate(string, int) string { return strings.Repeat("x", 300000) }
func New(...int) (string, error) { return strings.Repeat("x", 300000), nil }
func Must(...int) string { return strings.Repeat("x", 300000) }
GO
