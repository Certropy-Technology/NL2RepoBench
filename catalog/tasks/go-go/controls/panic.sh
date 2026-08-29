#!/usr/bin/env bash
set -euo pipefail

cat > go.mod <<'MOD'
module github.com/TheAlgorithms/Go

go 1.26.5
MOD
: > go.sum
mkdir -p vendor conversion
: > vendor/modules.txt
cat > conversion/conversion.go <<'GO'
package conversion

const Alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

func fail()                         { panic("panic control") }
func Base64Encode([]byte) string    { fail(); return "" }
func Base64Decode(string) []byte    { fail(); return nil }
func BinaryToDecimal(string) (int, error) { fail(); return 0, nil }
func Reverse(string) string         { fail(); return "" }
func DecimalToBinary(int) (string, error) { fail(); return "", nil }
func IntToRoman(int) (string, error) { fail(); return "", nil }
func RomanToInt(string) (int, error) { fail(); return 0, nil }
func HEXToRGB(uint) (byte, byte, byte) { fail(); return 0, 0, 0 }
func RGBToHEX(byte, byte, byte) uint { fail(); return 0 }
GO
