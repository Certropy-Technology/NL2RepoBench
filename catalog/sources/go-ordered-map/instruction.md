# Build `go-ordered-map`

## Project Description

Create a pure-Go module with module path `github.com/iancoleman/orderedmap` and
root package name `orderedmap`. It provides a JSON-capable map whose key order is
explicit and stable. The package must work on Linux/amd64 with Go 1.26.5.

The implementation is judged through public behavior. It may use any internal
representation, but it must preserve insertion order, support JSON round trips,
and expose the public types and methods below.

## Supports

- Use one root `go.mod` declaring exactly `github.com/iancoleman/orderedmap`.
- Include a `go.sum` file, even when it is empty. Use standard-library packages
  only; no external modules, cgo, plugins, `unsafe`, `go:generate`, workspaces,
  network access, or external services are needed.
- Build and test with `GOWORK=off`, `GOPROXY=off`, `GOSUMDB=off`,
  `GOTOOLCHAIN=local`, `GOOS=linux`, `GOARCH=amd64`, and `CGO_ENABLED=0`.
- The package is not required to make an uninitialized zero `OrderedMap` safe for
  `Set`; callers should use `New` before mutation. JSON unmarshalling into an
  `OrderedMap` pointer must initialize it as needed.

## API Usage Guide

All symbols below are in package `orderedmap`.

### `Pair` and `ByPair`

```go
type Pair struct{}
func (p *Pair) Key() string
func (p *Pair) Value() interface{}

type ByPair struct {
    Pairs []*Pair
    LessFunc func(a *Pair, b *Pair) bool
}
func (p ByPair) Len() int
func (p ByPair) Swap(i, j int)
func (p ByPair) Less(i, j int) bool
```

`Pair` exposes a key and its associated value through read-only methods. The
fields holding those values are intentionally not exported. `ByPair` adapts a
pair slice and comparison callback to Go's `sort.Interface`: `Len` reports the
slice length, `Swap` exchanges two entries, and `Less` delegates to `LessFunc`.

### `OrderedMap` construction and ordinary mutation

```go
func New() *OrderedMap
func (o *OrderedMap) SetEscapeHTML(on bool)
func (o *OrderedMap) Get(key string) (interface{}, bool)
func (o *OrderedMap) Set(key string, value interface{})
func (o *OrderedMap) Delete(key string)
func (o *OrderedMap) Keys() []string
func (o *OrderedMap) Values() map[string]interface{}
```

`New` returns an empty, usable map. `Set` adds a new key at the end; setting an
existing key replaces its value without moving the key. Keys are strings and
values may be any JSON-marshalable Go value (or any other Go value until it is
marshalled). `Get` returns the stored value and `true`, or the zero interface and
`false` for an absent key. `Delete` removes a key and is a no-op for an absent
key. `Keys` returns keys in their current order. `Values` returns the string-keyed
value map; its values are the same values returned by `Get`.

`SetEscapeHTML` changes the JSON encoder setting for this map. It is enabled by
default. When enabled, JSON string characters such as `<`, `>`, and `&` use the
same HTML-safe escaping as `encoding/json`; when disabled, those characters are
left unescaped. This setting is copied to nested ordered maps created while
decoding JSON.

### Ordering operations

```go
func (o *OrderedMap) SortKeys(sortFunc func(keys []string))
func (o *OrderedMap) Sort(lessFunc func(a *Pair, b *Pair) bool)
```

`SortKeys` gives the current key slice to the supplied function. `Sort` creates
`Pair` values for the current entries, orders them with the supplied less
function, and updates only the key order. A comparison function can inspect
`Pair.Key()` and `Pair.Value()`.

### JSON behavior

```go
func (o *OrderedMap) UnmarshalJSON(b []byte) error
func (o OrderedMap) MarshalJSON() ([]byte, error)
```

`MarshalJSON` emits an object with keys in `Keys()` order and values from the
map. Nested `OrderedMap` values use their own ordering and HTML setting. Empty
maps and empty arrays remain present. Invalid or unmarshalable values return a
JSON error rather than silently changing the order.

`UnmarshalJSON` accepts a JSON object and preserves the textual order of its
object keys. Use a map returned by `New` when decoding a complete replacement;
no special merge semantics are promised for pre-populated maps. JSON objects nested
inside objects or arrays are represented as `OrderedMap` values recursively;
other values follow the standard `encoding/json` decoding shapes (`float64`,
`string`, `bool`, `nil`, `[]interface{}`, and maps only where the decoder's
contract requires them). Duplicate object keys use the final decoded value and
the final occurrence's position in that object's key order. Escaped keys are
compared after JSON decoding, so their returned key strings are ordinary Go
strings. Malformed JSON returns the decoder error.

## Implementation Notes

Keep all behavior deterministic and bounded for ordinary inputs. Preserve key
order across `Set`, replacement, deletion, sorting, marshal, and unmarshal.
Use only caller-provided `io`-free JSON operations; this package does not read
or write files or use the network. Do not expose private tests, expected values,
or a source checkout to the implementation. The evaluator invokes the public API
through a separate, typed JSON subprocess bridge; the bridge must remain a
thin adapter and must not require any non-standard dependency.

