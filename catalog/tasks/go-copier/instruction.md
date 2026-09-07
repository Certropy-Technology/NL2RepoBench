# Recreate github.com/jinzhu/copier

## Project Description

Create a pure-Go module whose module path is exactly
`github.com/jinzhu/copier`. It must provide the public copying API of
`github.com/jinzhu/copier` for ordinary exported structs, slices, and maps.
The evaluator exercises the package through fixed, serializable Go scenarios;
it does not require a command-line program.

## Natural Language Instruction

Create the `github.com/jinzhu/copier` module from an empty `workspace/` and
implement its bounded public copying contract. Support exported struct fields,
pointer fields, slices, maps, case matching, zero-value filtering, deep copy,
field tags, field-name mappings, type converters, and invalid source or
destination errors. Keep ordinary shallow-copy aliasing unless `DeepCopy` is
explicitly enabled.

The implementation is a library and does not need a CLI. Reflection is an
implementation technique inside the candidate package; no reflection values,
callbacks, or database interfaces are sent through the fixed scenario bridge.

## Supports

- Linux/amd64 with Go `1.26.5`.
- A root `go.mod` with module path `github.com/jinzhu/copier`, Go directive
  `1.26.5`, an empty or valid `go.sum`, and `vendor/modules.txt`.
- Offline builds with `GOOS=linux`, `GOARCH=amd64`, `CGO_ENABLED=0`,
  `GOWORK=off`, `GOPROXY=off`, `GOSUMDB=off`, and `GOTOOLCHAIN=local`.
- A single pure-Go module. Do not use cgo, plugins, `unsafe`, a Go workspace,
  `replace` directives, network access, or external services.

## Project Directory Structure

```text
workspace/
├── go.mod
├── go.sum
├── vendor/
│   └── modules.txt
├── copier.go
├── copier_field.go
└── copier_map.go
```

Use the module path `github.com/jinzhu/copier` and root package name `copier`.
The root `.go` files may be organized differently when all documented exports
remain at the module root. Do not include verifier, generated test, or network
client code in the generated module.

## API Usage Guide

Implement package `copier` at the module root. The required public API is:

**Import path:** `import copier "github.com/jinzhu/copier"`.
In the API pseudocode below, the package identifier is introduced as `import copier`;
the quoted path above is the actual Go source form.

```go
type Option struct {
    IgnoreEmpty      bool
    CaseSensitive    bool
    DeepCopy         bool
    Converters       []TypeConverter
    FieldNameMapping []FieldNameMapping
    Must             bool
    NoPanic          bool
}

type TypeConverter struct {
    SrcType interface{}
    DstType interface{}
    Fn      func(src interface{}) (dst interface{}, err error)
}

type FieldNameMapping struct {
    SrcType interface{}
    DstType interface{}
    Mapping map[string]string
}

func Copy(toValue interface{}, fromValue interface{}) error
func CopyWithOption(toValue interface{}, fromValue interface{}, opt Option) error
```

The root package also exports `ErrInvalidCopyDestination`, `ErrInvalidCopyFrom`,
`ErrMapKeyNotMatch`, `ErrNotSupported`, and
`ErrFieldNameTagStartNotUpperCase`. These are error values suitable for
comparison or wrapping when their documented failure conditions occur.

`Copy` copies matching exported fields between compatible structs, values in
slices of structs, and values in maps when their keys and values are
assignable or convertible. The destination must be a non-nil, addressable
pointer. A nil or otherwise invalid source must return an error rather than
silently succeeding.

Field matching is case-insensitive by default. `Option{CaseSensitive: true}`
only copies an exact-name match. `Option{IgnoreEmpty: true}` leaves an existing
destination field unchanged when the corresponding source field is its Go zero
value. `Option{DeepCopy: true}` recursively copies pointer, slice, and map
contents so later mutation through the source does not change the copied value.

Destination tags are interpreted as follows:

- `copier:"-"` leaves that destination field unchanged.
- `copier:"SourceName"` copies from the exported source field named
  `SourceName`.
- `copier:"must,nopanic"` returns an error when the required source field is
  unavailable; `copier:"must"` may panic in that case.

`FieldNameMapping` remaps exported field names for the exact source and
destination types named in `SrcType` and `DstType`. Its `Mapping` maps source
field names to destination field names. `TypeConverter` is an optional caller
provided conversion hook: for matching source/destination dynamic types, call
`Fn` and assign its returned value, or return its error.

Examples:

```go
type Input struct { Name string; Age int }
type Output struct { Name string; Age int }

var out Output
err := copier.Copy(&out, Input{Name: "Ari", Age: 7})
// out is Output{Name: "Ari", Age: 7}

out = Output{Name: "keep", Age: 9}
err = copier.CopyWithOption(&out, Input{}, copier.Option{IgnoreEmpty: true})
// out remains Output{Name: "keep", Age: 9}
```

## Implementation Notes

The public API accepts arbitrary Go values, but the evaluator uses only bounded
ordinary structs, slices, maps, pointers, and scalar fields. It does not send
reflection values, callbacks, database drivers, private fields, or arbitrary
type descriptions across the subprocess boundary. Preserve normal Go pointer
and aliasing behavior unless `DeepCopy` is requested. Error text is not part of
the contract; errors must be non-nil and must not be fabricated as successful
copies.

## Examples

```go
type Source struct { Count int; Labels []string }
type Target struct { Count int; Labels []string }

var target Target
err := copier.CopyWithOption(&target, Source{Count: 2, Labels: []string{"a"}}, copier.Option{DeepCopy: true})
```

```go
type Tagged struct { Name string `copier:"DisplayName"` }
type Input struct { DisplayName string }
var tagged Tagged
_ = copier.Copy(&tagged, Input{DisplayName: "visible"})
```

## Error Handling and Boundary Conditions

- A nil destination, a non-pointer destination, or a nil source returns a
  non-nil error and must not partially claim success. Unsupported shapes use
  the exported error contract where applicable.
- Unexported fields are not copied. `IgnoreEmpty` preserves existing values,
  while ordinary copying writes compatible zero values. Mapping and converter
  callbacks are applied only to the declared type pairs, and converter errors
  propagate without being swallowed.
- Copying must not mutate the source. Deep-copied nested maps, slices, and
  pointers must not alias the source after the call. Every runtime phase is
  NoNetwork and deterministic.
