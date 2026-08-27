# Build a bounded govalidator library

## Project Description

Create the pure-Go module `github.com/asaskevich/govalidator/v12` at repository
root. Implement the deterministic string-validation and transformation surface
described below. The repository is evaluated through a newline-delimited JSON
bridge that is copied into the candidate module by the verifier.

## Supports

- Linux/amd64 with Go `1.26.5`.
- Exactly one root `go.mod` with module path
  `github.com/asaskevich/govalidator/v12`, a matching empty-or-valid `go.sum`,
  and no workspace or external `replace` directive.
- Pure Go with `CGO_ENABLED=0`; no cgo, plugins, generated code, unsafe code,
  network services, or external runtime dependencies.
- Offline builds with `GOOS=linux GOARCH=amd64 GOWORK=off GOPROXY=off
  GOSUMDB=off GOTOOLCHAIN=local` and `go build -mod=vendor`.

## API Usage Guide

Implement these public functions in package `govalidator`.

### Validators

The bridge operation `validate` accepts `[name, value]` and maps names to the
following exact one-string functions: `IsEmail`, `IsURL`, `IsRequestURL`,
`IsRequestURI`, `IsAlpha`, `IsUTFLetter`, `IsAlphanumeric`,
`IsUTFLetterNumeric`, `IsNumeric`, `IsUTFNumeric`, `IsUTFDigit`, `IsInt`,
`IsFloat`, `IsNull`, `IsNotNull`, `IsASCII`, `IsPrintableASCII`, `IsBase64`,
`IsDNSName`, `IsIP`, `IsIPv4`, `IsIPv6`, `IsPort`, `IsMAC`, `IsHost`,
`IsUUID`, `IsUUIDv3`, `IsUUIDv4`, `IsUUIDv5`, `IsJSON`, `IsHexadecimal`,
`IsHexcolor`, `IsRGBcolor`, `IsLatitude`, and `IsLongitude`.

Each returns a boolean. Preserve the upstream rules, including empty-string
behavior where the upstream function defines it. URL and host validation is
syntax-only; do not perform DNS, HTTP, or other I/O. The network-dependent
`IsExistingEmail` function is intentionally outside this bounded contract.

### String transformations

The bridge operation `transform` accepts `[name, value, parameters...]` and
supports `contains` (one parameter, returns a boolean), `matches` (one regular
expression, returns a boolean), `trim`, `left_trim`, `right_trim`, `blacklist`,
`whitelist`, `strip_low` (one boolean parameter), `replace_pattern` (pattern
and replacement), `camel_case_to_underscore`, `underscore_to_camel_case`,
`reverse`, `safe_file_name`, `normalize_email`, `get_lines`, and `get_line`
(one decimal index parameter). Functions returning errors must produce a
structured bridge error for invalid input.

### Converters

The bridge operation `convert` accepts `[name, JSON value]` and supports
`to_string`, `to_json`, `to_float`, and `to_int`. `to_boolean` accepts a
string in `[name, JSON string]`. Preserve the upstream conversion behavior,
including zero values and errors for unsupported or malformed values.

The bridge rejects any string longer than 64 KiB, any line index outside the
safe signed integer range, unknown operations, wrong argument counts, and
malformed JSON. It emits one JSON response per input line, never diagnostics to
stdout, and must not panic on malformed requests.

## Implementation Notes

Keep all public behavior deterministic and free of global-state mutation.
Unicode behavior must follow the package, while byte-length behavior must stay
distinct from rune-count behavior. Preserve regex semantics and JSON escaping.
Do not hard-code the evaluator's cases or add a second module. The bridge is a
transport adapter only; implement the package API rather than the bridge's
examples.
