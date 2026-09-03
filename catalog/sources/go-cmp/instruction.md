# Build a bounded go-cmp comparison library

## Project Description

Create the pure-Go `github.com/google/go-cmp/cmp` and
`github.com/google/go-cmp/cmp/cmpopts` packages at repository root. The
library compares Go values recursively and provides options for semantic
comparison. The task exercises deterministic equality, human-readable diffs,
reflection-safe handling of unexported fields, and common `cmpopts` options
through a typed subprocess bridge.

## Supports

- Linux/amd64 with Go `1.26.5`, `CGO_ENABLED=0`, and exactly one root `go.mod`
  whose module path is `github.com/google/go-cmp`.
- Offline builds with `GOOS=linux GOARCH=amd64 GOWORK=off GOPROXY=off
  GOSUMDB=off GOTOOLCHAIN=local` and `-mod=vendor`. There are no external
  modules in this frozen revision, but include `go.sum` and a valid vendor
  closure.
- Pure Go only. Do not use network services, cgo, plugins, generated code, or
  global mutable state to answer bridge requests.
- The bridge invokes only bounded JSON values and uses one request per line.
  It rejects malformed requests and must return structured errors without
  writing diagnostics to stdout.

## API Usage Guide

The main package is imported as `github.com/google/go-cmp/cmp`.

```go
func Equal(x, y any, opts ...Option) bool
func Diff(x, y any, opts ...Option) string
func Ignore() Option
func FilterPath(f func(Path) bool, opt Option) Option
func FilterValues(f any, opt Option) Option
func Transformer(name string, f any) Option
func Comparer(f any) Option
func Exporter(f func(reflect.Type) bool) Option
func AllowUnexported(types ...any) Option
```

`Equal` recursively compares values and returns whether they are semantically
equal. `Diff` returns a pseudo-Go textual difference (`-` for values removed
from the first input and `+` for values added to the second); equal values
produce an empty string. Options are immutable comparison configuration. A
comparer or transformer must be deterministic and type-compatible. An
ambiguous set of applicable options, invalid callbacks, or an attempt to
compare unexported fields without an `Ignore`/`Exporter` policy may panic, as
documented by the upstream package.

`Path` is a read-only sequence of `PathStep` values. `PathStep` implementations
include `StructField`, `SliceIndex`, `MapIndex`, `Indirect`, `TypeAssertion`,
and `Transform`. Their `String`, `Type`, and `Values` methods expose the
current traversal location to a path filter or reporter.

The helper package is imported as
`github.com/google/go-cmp/cmp/cmpopts` and must provide these constructors:

```go
func EquateEmpty() cmp.Option
func EquateApprox(fraction, margin float64) cmp.Option
func EquateNaNs() cmp.Option
func EquateApproxTime(margin time.Duration) cmp.Option
func EquateErrors() cmp.Option
func EquateComparable(types ...any) cmp.Option
func SortSlices(lessOrCompareFunc any) cmp.Option
func SortMaps(lessOrCompareFunc any) cmp.Option
```

`EquateEmpty` equates nil and empty maps/slices of the same type.
`EquateApprox` accepts non-negative fraction and margin and compares finite
float32/float64 values within `max(fraction*min(abs(x),abs(y)), margin)`.
`EquateNaNs` treats two NaN values as equal. `SortSlices` and `SortMaps` copy
and stably sort values using a deterministic less or three-way compare
function before recursive comparison. Invalid option arguments must preserve
the package's documented panic behavior.

The evaluator uses these bridge operations: `equal_profiles`, `equal_floats`,
`equal_strings_sorted`, `equal_maps_sorted`, `diff_values`, and
`equal_exported`. Their JSON argument and result shapes are private test
details; implement the public Go APIs rather than matching example strings.

## Implementation Notes

Preserve recursive behavior for structs, arrays, slices, maps, pointers,
interfaces, and scalar values. Keep map and slice nil-ness meaningful unless
an option changes it. Do not hard-code evaluator fixtures or emit a trusted
reward/report from candidate code. The bridge is the only adapter boundary:
the verifier runs it as a separate candidate-owned subprocess and does not
import candidate packages into the trusted Python process.
