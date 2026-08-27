# Build `go-humanize`

## Project Description

Create a pure-Go module that provides deterministic human-readable formatting
helpers. The repository must use module path `github.com/dustin/go-humanize`
and expose the root package `humanize` plus its `english` subpackage.

## Supports

- Linux/amd64 with Go 1.26.5.
- A single root `go.mod` and `go.sum`; build with `GOWORK=off`, `GOPROXY=off`,
  `GOSUMDB=off`, `GOTOOLCHAIN=local`, and `CGO_ENABLED=0`.
- Pure Go only. Do not use cgo, plugins, `unsafe`, external `replace`
  directives, workspaces, generated source, network access, or external services.

## API Usage Guide

Implement these public functions with deterministic output and the exact
signatures below.

Root package `humanize` at import path `github.com/dustin/go-humanize`:

```go
func Bytes(s uint64) string
func IBytes(s uint64) string
func Comma(v int64) string
func Ftoa(num float64) string
func FtoaWithDigits(num float64, digits int) string
func Ordinal(x int) string
func SI(input float64, unit string) string
func SIWithDigits(input float64, decimals int, unit string) string
```

`Bytes` uses decimal units and renders values such as `82854982` as
`83 MB`; `IBytes` uses binary units and renders that value as `79 MiB`.
Values below ten are rendered as `<number> B`; unit values at an exact power
of a base may retain one decimal place, as in `1.0 GB` and `1.0 KiB`.
`Comma` inserts separators every three decimal digits, including for negative
values and the minimum signed 64-bit integer. `Ftoa` formats a float with at most six decimal places
and removes trailing zeroes; `FtoaWithDigits` additionally limits the decimal
places to the requested non-negative count. `Ordinal` appends the English
ordinal suffix, including the 11th, 12th, and 13th exceptions; it follows
Go's signed remainder behavior for negative inputs.

`SI` chooses the appropriate SI prefix for a number and returns the formatted
value, a space, the prefix, and the supplied unit. `SIWithDigits` behaves the
same way while limiting the value's decimal places. Zero has an empty prefix;
negative values retain their sign. Prefixes include milli (`m`), micro (`µ`),
kilo (`k`), mega (`M`), giga (`G`), and larger or smaller SI prefixes used by
the package.

English subpackage `english` at import path
`github.com/dustin/go-humanize/english`:

```go
func Plural(quantity int, singular, plural string) string
func PluralWord(quantity int, singular, plural string) string
```

When `quantity == 1`, both functions use the singular word. For other
quantities an explicitly supplied plural is used. With an empty plural,
common irregular words such as `index`, `matrix`, and `vertex` use their
standard forms; regular words use the package's simple English rules. `Plural`
also formats the quantity with comma separators and joins it to the selected
word with one space.

Inputs must be handled without panics, global mutable state, or retained input
storage. The functions return strings and do not perform I/O.

## Implementation Notes

Keep the module self-contained and compatible with the signatures above.
Numerical boundary behavior, rounding, sign handling, Unicode micro prefix,
empty strings, explicit plurals, and irregular plural words are part of the
public behavior. The evaluation calls the API through a bounded JSON
subprocess bridge; it does not import candidate code into the trusted verifier.
