# Recreate github.com/jinzhu/copier

## Project Description

Create a pure-Go module whose module path is exactly
`github.com/jinzhu/copier`. It must provide the public copying API of
`github.com/jinzhu/copier` for ordinary exported structs, slices, and maps.
The evaluator exercises the package through fixed, serializable Go scenarios;
it does not require a command-line program.

## Supports

- Linux/amd64 with Go `1.26.5`.
- A root `go.mod` with module path `github.com/jinzhu/copier`, Go directive
  `1.26.5`, an empty or valid `go.sum`, and `vendor/modules.txt`.
- Offline builds with `GOOS=linux`, `GOARCH=amd64`, `CGO_ENABLED=0`,
  `GOWORK=off`, `GOPROXY=off`, `GOSUMDB=off`, and `GOTOOLCHAIN=local`.
- A single pure-Go module. Do not use cgo, plugins, `unsafe`, a Go workspace,
  `replace` directives, network access, or external services.

## API Usage Guide

Implement package `copier` at the module root. The required public API is:

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
