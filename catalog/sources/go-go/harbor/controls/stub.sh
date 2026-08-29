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

func Base64Encode([]byte) string                 { return "" }
func Base64Decode(string) []byte                 { return []byte{} }
func BinaryToDecimal(string) (int, error)        { return 0, nil }
func Reverse(string) string                      { return "" }
func DecimalToBinary(int) (string, error)        { return "", nil }
func IntToRoman(int) (string, error)              { return "", nil }
func RomanToInt(string) (int, error)              { return 0, nil }
func HEXToRGB(uint) (byte, byte, byte)            { return 0, 0, 0 }
func RGBToHEX(red, green, blue byte) (hex uint)   { return 0 }
GO
