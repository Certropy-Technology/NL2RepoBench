# Build a bounded govalidator library

## Project Description

Create the pure-Go module `github.com/asaskevich/govalidator/v12` at repository
root. Implement the deterministic string-validation and transformation surface
described below. The repository is evaluated through a newline-delimited JSON
bridge that is copied into the candidate module by the verifier.

## Natural Language Instruction

Create the pure-Go `github.com/asaskevich/govalidator/v12` module from an empty
workspace. Implement the documented validators, string transformations, and
JSON-safe converters with deterministic Unicode, regex, error, and ordering
behavior. Keep the package free of I/O, network access, and global state.

## Supports

- Linux/amd64 with Go `1.26.5`.
- Exactly one root `go.mod` with module path
  `github.com/asaskevich/govalidator/v12`, a matching empty-or-valid `go.sum`,
  and no workspace or external `replace` directive.
- Pure Go with `CGO_ENABLED=0`; no cgo, plugins, generated code, unsafe code,
  network services, or external runtime dependencies.
- Offline builds with `GOOS=linux GOARCH=amd64 GOWORK=off GOPROXY=off
  GOSUMDB=off GOTOOLCHAIN=local` and `go build -mod=vendor`.

## Project Directory Structure

```text
workspace/
├── go.mod
├── go.sum
├── vendor/modules.txt
├── validator.go
├── transforms.go
└── conversion.go
```

The module path is `github.com/asaskevich/govalidator/v12` and the public
package name is `govalidator`. The JSON bridge is a transport adapter, not a
replacement for the library implementation.

## API Usage Guide

Implement these public functions in package `govalidator`.

```go
import govalidator "github.com/asaskevich/govalidator/v12"

ok := govalidator.IsEmail("user@example.com")
```

### Validators

The bridge operation `validate` accepts `[name, value]` and maps names to the
following exact one-string functions. Every function has the signature
`func Name(str string) bool`:

```text
IsEmail              IsURL             IsRequestURL       IsRequestURI
IsAlpha              IsUTFLetter       IsAlphanumeric    IsUTFLetterNumeric
IsNumeric            IsUTFNumeric      IsUTFDigit         IsInt
IsFloat              IsNull            IsNotNull          IsASCII
IsPrintableASCII     IsBase64          IsDNSName          IsIP
IsIPv4               IsIPv6            IsPort             IsMAC
IsHost               IsUUID            IsUUIDv3           IsUUIDv4
IsUUIDv5             IsJSON            IsHexadecimal      IsHexcolor
IsRGBcolor           IsLatitude        IsLongitude
```

Each returns a boolean. Preserve the upstream rules, including empty-string
behavior where the upstream function defines it. URL and host validation is
syntax-only; do not perform DNS, HTTP, or other I/O. The network-dependent
`IsExistingEmail` function is intentionally outside this bounded contract.
The ASCII-only alpha, alphanumeric, numeric, integer, ASCII, and printable
ASCII predicates accept the empty string. Their UTF variants use Unicode
letter, number, or decimal-digit classes as named. `IsIP` accepts either IP
version, `IsHost` accepts an IP address or DNS name, and `IsPort` accepts the
decimal range 1 through 65535. UUID-specific predicates check the version
nibble. Latitude and longitude include their endpoints and reject values
outside `[-90, 90]` and `[-180, 180]` respectively.

### String transformations

The bridge operation `transform` accepts `[name, value, parameters...]` and
supports these package functions:

```go
func Contains(str, substring string) bool
func Matches(str, pattern string) bool
func Trim(str, chars string) string
func LeftTrim(str, chars string) string
func RightTrim(str, chars string) string
func BlackList(str, chars string) string
func WhiteList(str, chars string) string
func StripLow(str string, keepNewLines bool) string
func ReplacePattern(str, pattern, replace string) string
func CamelCaseToUnderscore(str string) string
func UnderscoreToCamelCase(str string) string
func Reverse(str string) string
func SafeFileName(str string) string
func NormalizeEmail(str string) (string, error)
func GetLines(str string) []string
func GetLine(str string, index int) (string, error)
```

`Matches` and `ReplacePattern` use Go regular-expression syntax; `Matches`
returns false for an invalid expression. An empty `chars` argument makes the
three trim functions remove whitespace. `BlackList` removes matching
characters, while `WhiteList` removes nonmatching characters. `StripLow`
removes control bytes below 32 and byte 127, preserving carriage return and
newline only when requested. `Reverse` reverses Unicode runes rather than raw
UTF-8 bytes. `GetLines` splits on `"\n"`, and `GetLine` returns an error for an
index outside the resulting slice.

`SafeFileName` removes directory components, lowercases the base name, replaces
spaces with hyphens, and removes characters unsafe for a simple file name.
`NormalizeEmail` validates the address and lowercases the host. For Gmail it
also lowercases the local part, removes dots and plus tags, and maps
`googlemail.com` to `gmail.com`. The `get_line` bridge parameter is a base-10
index encoded as a string. Functions returning errors produce a structured
bridge error for invalid input.

### Converters

The bridge operation `convert` accepts `[name, JSON value]` and supports
these package functions:

```go
func ToString(value any) string
func ToJSON(value any) (string, error)
func ToFloat(value any) (float64, error)
func ToInt(value any) (int64, error)
func ToBoolean(value string) (bool, error)
```

The operation names are `to_string`, `to_json`, `to_float`, `to_int`, and
`to_boolean`. `ToJSON` uses the standard JSON encoding without added
indentation. Numeric conversion accepts Go numeric values and numeric strings,
with errors for malformed or unsupported values. Boolean conversion uses
Go's accepted boolean strings, including `true`, `false`, `1`, `0`, and their
documented case variants.

The bridge rejects any string longer than 64 KiB, any line index outside the
safe signed integer range, unknown operations, wrong argument counts, and
malformed JSON. It emits one JSON response per input line, never diagnostics to
stdout, and must not panic on malformed requests.

## Examples

```go
if govalidator.IsIPv4("192.0.2.1") {
    // accept the syntax-only IPv4 form
}
```

```go
lines := govalidator.GetLines("first\nsecond")
line, err := govalidator.GetLine("first\nsecond", 1)
```

## Error Handling and Boundary Conditions

Invalid regular expressions return the documented false/error result rather
than panicking. Empty strings, Unicode runes, malformed JSON, unsupported
conversions, oversized bridge strings, and out-of-range indexes follow the
contracts above; diagnostics stay off stdout.

## Implementation Notes

Keep all public behavior deterministic and free of global-state mutation.
Unicode behavior must follow the package, while byte-length behavior must stay
distinct from rune-count behavior. Preserve regex semantics and JSON escaping.
Do not hard-code the evaluator's cases or add a second module. The bridge is a
transport adapter only; implement the package API rather than the bridge's
examples.
