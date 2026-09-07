# Build a bounded go-cmp comparison library

## Project Description

Create the pure-Go `github.com/google/go-cmp/cmp` and
`github.com/google/go-cmp/cmp/cmpopts` packages at the repository root. The
library compares Go values recursively and provides options that change the
meaning of equality. The task exercises deterministic equality, human-readable
diffs, reflection-safe handling of unexported fields, path and value filtering,
transformations, custom comparers, and the common `cmpopts` helpers, all
through a typed subprocess bridge.

## Supports

- Linux/amd64 with Go `1.26.5`, `CGO_ENABLED=0`, and exactly one root `go.mod`
  whose module path is `github.com/google/go-cmp`.
- Offline builds with `GOOS=linux GOARCH=amd64 GOWORK=off GOPROXY=off
  GOSUMDB=off GOTOOLCHAIN=local` and `-mod=vendor`. There are no external
  modules in this frozen revision, but keep `go.sum` and a valid vendor closure.
- Pure Go only. Do not use network services, cgo, plugins, generated code, or
  global mutable state to answer bridge requests.
- The bridge invokes only bounded JSON values and uses one request per line.
  It rejects malformed requests and must return structured errors without
  writing diagnostics to stdout.

## Natural Language Instruction

Build the bounded `github.com/google/go-cmp/cmp` module from an empty workspace.
Implement recursive comparison, diffs, filtering, transformations, custom
comparers, and `cmpopts` helpers exactly as described below.

## Project Directory Structure

```text
workspace/
├── go.mod
├── go.sum
├── vendor/modules.txt
├── cmp/
│   ├── compare.go
│   ├── options.go
│   └── path.go
└── cmpopts/
    └── options.go
```

Preserve both import paths and root package names. Do not add private verifier
or hidden-test material.

## Examples

```go
equal := cmp.Equal(struct{A int}{1}, struct{A int}{1})
diff := cmp.Diff([]int{1}, []int{2})
```

```go
equal := cmp.Equal(valuesA, valuesB, cmpopts.EquateEmpty())
```

## Error Handling and Boundary Conditions

Preserve handling of unexported fields, nil values, option conflicts, filtered
paths/values, transformations, deterministic diffs, and unsupported values.
Avoid global mutable state and network access.

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

`Equal` reports whether two values are semantically equal and `Diff` returns a
pseudo-Go textual difference (`-` marks a value removed from the first input,
`+` marks a value added by the second). Equal values produce an empty `Diff`.
A non-empty `Diff` names the path of every difference, so a struct field named
`Name`, a map key such as `"env"`, and a slice element all appear in the
rendered text together with their enclosing field names.

Options are immutable comparison configuration. The signature of each
option constructor is part of the contract:

- `Comparer(f)` accepts `func(T, T) bool` and defines equality for values
  assignable to `T`. The function must be symmetric, deterministic, and pure.
- `Transformer(name, f)` accepts `func(T) R`, converts values of type `T` to
  type `R`, and compares the results. It must not mutate `T`. `name` labels the
  transformation step in the path and diff output.
- `FilterPath(f, opt)` applies `opt` only at paths where `f` returns true for
  the current `Path`. `FilterValues(f, opt)` applies `opt` only to value pairs
  where `f`, a `func(T, T) bool`, returns true. In both cases `opt` may be
  `Ignore`, `Transformer`, `Comparer`, `Options`, or an already filtered option.
- `Ignore` causes every comparison it is applied to to report equality. It is
  only meaningful combined with `FilterPath` or `FilterValues`; passing an
  unfiltered `Ignore()` to `Equal` or `Diff` is a programming error and panics.
- `AllowUnexported(types...)` permits comparison of unexported fields for the
  given struct types only. `Exporter(f)` permits unexported-field introspection
  for every type `t` where `f(t)` returns true. Without such a policy,
  comparing a value that contains unexported fields panics.

`Path` is a read-only sequence of `PathStep` values. `PathStep` implementations
include `StructField`, `SliceIndex`, `MapIndex`, `Indirect`, `TypeAssertion`,
and `Transform`; their `String`, `Type`, and `Values` methods expose the current
traversal location to a path filter.

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

- `EquateEmpty` equates nil and empty maps and slices of the same type.
- `EquateApprox` accepts non-negative `fraction` and `margin` and reports
  finite `float32`/`float64` values equal when
  `|x-y| <= max(fraction*min(|x|,|y|), margin)`. It is not used when either
  value is NaN or infinite.
- `EquateNaNs` reports two NaN values as equal. It combines with `EquateApprox`.
- `EquateApproxTime` accepts a non-negative margin and reports two non-zero
  `time.Time` values equal when they are within that margin of each other.
- `EquateErrors` reports two non-nil errors equal when `errors.Is` matches them
  in either direction, so a wrapped error equals its target; two unrelated
  error values stay unequal. A nil error never equals a non-nil error.
- `EquateComparable(types...)` reports values of the given comparable types
  equal using the `==` operator instead of recursing into their fields.
- `SortSlices` and `SortMaps` copy and stably sort the elements or entries with
  a deterministic less or three-way compare function before comparing.

Invalid option arguments (negative fraction, margin, or a malformed comparer)
must preserve the package's documented panic behavior.

The evaluator drives these bridge operations: `equal_profiles`,
`equal_floats`, `equal_strings_sorted`, `equal_maps_sorted`, `diff_values`,
`diff_profile_paths`, `equal_exported`, `equal_exporter`,
`equal_ignore_unfiltered`, `equal_comparable`, `equal_filter_path`,
`equal_filter_values`, `equal_transformer`, `equal_comparer`, `equal_errors`,
and `equal_times`. Only the public Go APIs above determine their results; do
not match example strings or hard-code evaluator fixtures.

## Implementation Notes

Preserve recursive behavior for structs, arrays, slices, maps, pointers,
interfaces, and scalar values. Keep map and slice nil-ness meaningful unless an
option changes it. The option set applied to a value pair must be
unambiguous: an applicable `Comparer` or `Transformer` for the concrete type is
used, and conflicting options for the same type panic as documented. Do not
hard-code evaluator fixtures or emit a trusted reward/report from candidate
code. The bridge is the only adapter boundary: the verifier installs its own
read-only copy of the bridge, builds it as `cmd/bridge` inside the candidate
module, and runs it as a separate candidate-owned subprocess with bounded CPU,
wall time, output, and process-group cleanup. The verifier never imports
candidate packages into the trusted Python process.
