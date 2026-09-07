# Build a deterministic Go merge library

## Project Description

Create the Go module `dario.cat/mergo` at the repository root. It is a pure-Go
reflection helper for filling zero-valued fields and entries in destination
structs, maps, and slices from a source value. The evaluator exercises the
root package through a typed JSON subprocess bridge. Implement the package
from an empty workspace; do not assume that source files or a bridge are
provided.

## Natural Language Instruction

Create the pure-Go module `dario.cat/mergo` from an empty workspace. Implement
the public merge and map APIs, option functions, configuration type,
transformer interface, and stable exported errors described below. The package
must work for typed callers using `reflect.Value` and for bounded bridge inputs
that represent JSON-compatible structs, maps, and slices.

The required capability groups are:

1. Zero-value struct, map, slice, pointer, and nested-value merging.
2. Overwrite, empty-value, append, deep-copy, dereference, type-check, and
   transformer options with order-sensitive configuration.
3. Struct-to-map and map-to-struct conversion with deterministic key naming.
4. Stable error values for nil, type, destination-kind, and unsupported cases.
5. A module-root package that builds offline with the specified Go toolchain.

Do not add a second public package, a command-line interface, a network
client, cgo, or mutable process-global state. The evaluator supplies its own
bridge; the library itself remains the root importable package.

## Supports

- Linux/amd64 with Go `1.26.5`, one root `go.mod`, and module path
  `dario.cat/mergo`.
- Build with
  `GOOS=linux GOARCH=amd64 CGO_ENABLED=0 GOWORK=off GOPROXY=off
  GOSUMDB=off GOTOOLCHAIN=local go build -mod=vendor ./cmd/bridge`.
- The module has no third-party dependencies. Include `go.mod`, `go.sum`, and
  the offline vendor layout needed for `-mod=vendor`; do not use cgo, plugins,
  generated code, external services, or a workspace file.
- The public package is imported as `dario.cat/mergo`. Keep the exported root
  API and error values compatible with the guide below.

## Project Directory Structure

```text
workspace/
├── go.mod
├── go.sum
├── merge.go
├── map.go
├── config.go
├── errors.go
└── internal/
    └── reflection.go
```

The module path in `go.mod` is `dario.cat/mergo`; callers import the root
package from that path. This is a concrete target layout. The implementation
may combine files, but exported declarations remain in the root package and
reflection helpers must not become a new public API. The evaluator bridge is
not part of the generated project. A vendor directory is optional for this
zero-dependency module, but the specified offline build command must continue
to work.

## API Usage Guide

### Merging equal types

```go
func Merge(dst, src interface{}, opts ...func(*Config)) error
func MergeWithOverwrite(dst, src interface{}, opts ...func(*Config)) error
```

`dst` must be a non-nil pointer to a struct, map, or slice. `src` may be the
same value type or a pointer to it. Without options, recursively copy only
non-empty source values into zero-valued destination fields or entries;
existing destination values remain unchanged. Exported struct fields are
eligible and unexported fields must remain untouched. Maps merge their keys;
maps and structs nested inside addressable values are traversed where the
underlying Go value permits it. A nil argument returns `ErrNilArguments`, a
non-pointer destination returns `ErrNonPointerArgument`, different types
return `ErrDifferentArgumentsTypes`, and unsupported kinds return
`ErrNotSupported`.

`MergeWithOverwrite` is equivalent to `Merge` with `WithOverride` appended:
non-empty source values replace existing destination values. Source empty
values are still not copied unless `WithOverwriteWithEmptyValue` is also
used. Successful calls mutate `dst` and return nil.

### Options and configuration

The following option functions have signature `func(*Config)` and may be
passed to `Merge` or `Map`:

```go
func WithOverride(config *Config)
func WithOverwriteWithEmptyValue(config *Config)
func WithOverrideEmptySlice(config *Config)
func WithoutDereference(config *Config)
func WithAppendSlice(config *Config)
func WithTypeCheck(config *Config)
func WithSliceDeepCopy(config *Config)
func WithTransformers(transformers Transformers) func(*Config)
```

`WithOverride` replaces non-empty destination values. `WithAppendSlice`
appends same-typed source slices instead of replacing them. The append option
must reject different slice types. `WithOverwriteWithEmptyValue` permits empty
source values to overwrite and removes destination map keys absent from the
source. `WithOverrideEmptySlice` allows an empty source slice to replace an
empty destination slice. `WithoutDereference` treats a non-nil pointer as
non-empty and prevents recursive pointer dereferencing for the merge decision.
`WithTypeCheck` requests a type check for slice replacement. `WithSliceDeepCopy`
merges slice elements with overwrite semantics. Options are applied in order.

`Config` exposes the public field `Transformers`, `Overwrite`,
`ShouldNotDereference`, `AppendSlice`, and `TypeCheck`. `Transformers` is the
interface:

```go
type Transformers interface {
    Transformer(reflect.Type) func(dst, src reflect.Value) error
}
```

Transformer callbacks operate in-process with `reflect.Value`; they are part
of the public API but are outside the JSON bridge boundary.

### Mapping structs and maps

```go
func Map(dst, src interface{}, opts ...func(*Config)) error
func MapWithOverwrite(dst, src interface{}, opts ...func(*Config)) error
```

`Map` maps a `map[string]interface{}` into a pointer to a struct, or a struct
into a pointer to `map[string]interface{}`. Struct field names become lower
camel-case map keys; unexported fields are ignored. Struct and map values are
merged recursively according to the same zero-value and option rules. Equal
kind arguments are handled like `Merge`. An invalid destination kind returns
`ErrExpectedMapAsDestination` or `ErrExpectedStructAsDestination`, as
appropriate. `MapWithOverwrite` adds `WithOverride`.

### Errors and determinism

The exported errors are variables whose messages are stable:

```go
var ErrNilArguments error
var ErrDifferentArgumentsTypes error
var ErrNotSupported error
var ErrExpectedMapAsDestination error
var ErrExpectedStructAsDestination error
var ErrNonPointerArgument error
```

Calls are deterministic for the same typed inputs and options. The package
must not print diagnostics or depend on network, clock, randomness, or
process-global mutable state. Do not add a `main` package; the evaluator adds
its own bridge under `cmd/bridge`.

## Implementation Notes

Use pointer receivers only where mutation requires them and preserve the
caller-owned destination. Reflection must never panic for documented inputs,
including nil pointers and empty maps/slices. Preserve map values that are
not overwritten, copy slices only according to the selected option, and do
not write unexported fields. The bridge uses bounded newline-delimited JSON
requests and serializes only values that are representable without callbacks
or native reflection objects.

## Examples

```go
package main

import mergo "dario.cat/mergo"

type Destination struct { Name string; Count int }
dst := &Destination{Name: "old"}
src := Destination{Count: 3}
err := mergo.Merge(dst, src)
```

```go
package main

import mergo "dario.cat/mergo"

dst := map[string]interface{}{"keep": 1}
src := map[string]interface{}{"new": 2}
err := mergo.Map(&dst, src, mergo.WithOverwriteWithEmptyValue)
```

```go
package main

import mergo "dario.cat/mergo"

dst := []int{1}
src := []int{2, 3}
err := mergo.Merge(&dst, src, mergo.WithAppendSlice)
```

## Error Handling and Boundary Conditions

- A nil source or destination returns `ErrNilArguments`; a destination that
  is not a non-nil pointer returns `ErrNonPointerArgument` without mutation.
- Different source and destination types return `ErrDifferentArgumentsTypes`.
  Unsupported kinds and invalid map/struct destination directions return the
  documented stable error variables rather than a reflection panic.
- Without overwrite, existing non-empty destination values and map entries
  remain unchanged. Empty source values are ignored unless the matching empty
  overwrite option is present.
- Slice append and deep-copy options preserve element order and reject
  incompatible slice types. Options are applied in the order supplied by the
  caller.
- Unexported struct fields are never written. Calls with the same typed inputs
  and options produce the same destination and error result; no clock,
  randomness, process state, or network is consulted.
