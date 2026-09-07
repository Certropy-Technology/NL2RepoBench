# Build TheAlgorithms/Go conversion package

## Project Description

Create a pure-Go module that implements the deterministic public conversion
APIs from `TheAlgorithms/Go`. The repository must be a single Go module whose
module path is `github.com/TheAlgorithms/Go`. Implement package `conversion`
at import path `github.com/TheAlgorithms/Go/conversion`.

This task covers RFC 4648 Base64, binary and decimal integers, rune-aware
string reversal, Roman numerals, and packed RGB colors. Other packages from
the upstream algorithms repository are out of scope.

## Supports

- Linux/amd64 with Go 1.26.5.
- A root `go.mod` declaring module `github.com/TheAlgorithms/Go` and Go
  `1.26.5`, a root `go.sum`, and `vendor/modules.txt`.
- Builds with `GOOS=linux`, `GOARCH=amd64`, `CGO_ENABLED=0`, `GOWORK=off`,
  `GOPROXY=off`, `GOSUMDB=off`, and `GOTOOLCHAIN=local`.
- One pure-Go module with no third-party dependencies. Do not use cgo,
  plugins, `unsafe`, `go generate`, a Go workspace, external `replace`
  directives, network access, or external services.

## Natural Language Instruction

Build the pure-Go `github.com/TheAlgorithms/Go` module from an empty workspace.
Implement the `conversion` package's deterministic base64, integer, string,
Roman numeral, and packed RGB conversions listed below.

## Project Directory Structure

```text
workspace/
├── go.mod
├── go.sum
├── vendor/modules.txt
└── conversion/
    └── conversion.go
```

Expose the package at `github.com/TheAlgorithms/Go/conversion`; other upstream
algorithms and private verifier files are out of scope.

## Examples

```go
encoded := conversion.EncodeBase64("hello")
decoded, err := conversion.DecodeBase64(encoded)
```

```go
roman, err := conversion.ToRoman(42)
```

## Error Handling and Boundary Conditions

Preserve invalid base64, numeric overflow, unsupported Roman values, Unicode
runes, RGB component bounds, and deterministic formatting rules in the API
guide. No external service or mutable global state is allowed.

## API Usage Guide

Implement the following declarations in package `conversion`:

```go
const Alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

func Base64Encode(input []byte) string
func Base64Decode(input string) []byte
func BinaryToDecimal(binary string) (int, error)
func Reverse(str string) string
func DecimalToBinary(num int) (string, error)
func IntToRoman(n int) (string, error)
func RomanToInt(input string) (int, error)
func HEXToRGB(hex uint) (red, green, blue byte)
func RGBToHEX(red, green, blue byte) (hex uint)
```

### Base64

`Base64Encode` and `Base64Decode` implement the standard RFC 4648 Base64
alphabet declared by `Alphabet`. Encoding uses `=` padding and returns an
empty string for empty input. `Base64Decode` is required for well-formed,
padded RFC 4648 input whose length is a multiple of four; it returns the
original bytes, including arbitrary UTF-8 bytes. Malformed Base64 input is
outside this task's input domain.

```go
encoded := Base64Encode([]byte("Go!"))
decoded := Base64Decode(encoded)
fmt.Println(encoded, string(decoded))
// R28h Go!
```

### Binary, decimal, and strings

`BinaryToDecimal` accepts a non-empty string of only `0` and `1`, up to 32
digits. It returns the corresponding non-negative `int`. An empty string,
another character, or more than 32 digits returns a non-nil error and value
`-1`.

`DecimalToBinary` accepts a non-negative `int` and returns its shortest binary
representation without a prefix or leading zeroes. Zero returns `"0"`.
Negative input returns a non-nil error and an empty string.

`Reverse` reverses a string by Unicode code point, not by byte. It preserves
the bytes of each UTF-8 encoded rune. It returns an empty string for empty
input.

### Roman numerals

`IntToRoman` accepts integers from 1 through 3999 and returns uppercase,
canonical Roman notation using the standard subtractive pairs `IV`, `IX`,
`XL`, `XC`, `CD`, and `CM`. Values outside that range return a non-nil error
and an empty string.

`RomanToInt` accepts canonical uppercase Roman representations in the same
range and returns their integer value. The empty string returns `0` without an
error. Inputs containing unsupported characters, lowercase letters, or token
order that cannot be consumed return a non-nil error and value `0`.

### RGB colors

`RGBToHEX` packs red, green, and blue into bits 16-23, 8-15, and 0-7 of a
`uint`, respectively. `HEXToRGB` performs the inverse and ignores bits above
the low 24 bits.

```go
r, g, b := HEXToRGB(0x3498db)
packed := RGBToHEX(r, g, b)
fmt.Printf("%d %d %d %#x\n", r, g, b, packed)
// 52 152 219 0x3498db
```

## Implementation Notes

All operations must be deterministic, must not mutate global state during
ordinary calls, and must not retain references to caller-owned input. Keep
the package usable by normal Go callers; do not implement a command-line-only
facade. Errors may use any stable, non-empty message because callers rely on
the non-nil error contract rather than exact wording.
