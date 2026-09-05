# Build a deterministic radix tree

## Project Description

Create the pure-Go package `github.com/armon/go-radix` and implement its
public radix-tree dictionary API. The task focuses on exact key lookup,
longest-prefix lookup, ordered traversal, and mutation of an in-memory tree.
The package does not need a command-line interface, persistence, concurrency,
or external services.

## Supports

- Linux/amd64 with Go 1.26.5, `CGO_ENABLED=0`, and a single root `go.mod`.
- A module path of `github.com/armon/go-radix`, a `go 1.26.5` directive, a
  matching `go.sum`, and a vendor-compatible module layout.
- String keys and JSON-compatible values. Values are opaque to the tree and
  may be nil, booleans, strings, numbers, arrays, or maps.
- Bounded in-memory calls. The evaluation bridge limits each request to 64
  entries or keys and 256 KiB per newline-delimited JSON request.
- Deterministic behavior for the same insertion sequence. The tree must not
  require files, clocks, random state, network access, or cgo.

## Natural Language Instruction

Build the pure-Go `github.com/armon/go-radix` module from an empty workspace.
Implement the root `radix` tree, constructors, exact lookup, prefix lookup,
ordered walking, snapshots, and deletion operations in the API guide.

## Project Directory Structure

```text
workspace/
├── go.mod
├── go.sum
├── vendor/modules.txt
└── radix.go
```

The package is imported as `github.com/armon/go-radix`; preserve the exported
`Tree` and `WalkFn` contracts. Do not add private evaluation files.

## Examples

```go
tree := radix.New(); old, updated := tree.Insert("app/api", 7)
value, ok := tree.Get("app/api")
```

```go
key, value, ok := tree.LongestPrefix("app/api/v1/users")
```

## Error Handling and Boundary Conditions

Preserve empty keys and values, replacement return values, missing-key results,
lexicographic walk order, prefix/path boundaries, delete counts, and independent
`ToMap` snapshots. Methods must not require a service, clock, or network.

## API Usage Guide

Implement package `radix` at import path `github.com/armon/go-radix` with the
following public API:

```go
type WalkFn func(s string, v interface{}) bool

type Tree struct

func New() *Tree
func NewFromMap(m map[string]interface{}) *Tree

func (t *Tree) Len() int
func (t *Tree) Insert(s string, v interface{}) (interface{}, bool)
func (t *Tree) Get(s string) (interface{}, bool)
func (t *Tree) Delete(s string) (interface{}, bool)
func (t *Tree) DeletePrefix(s string) int
func (t *Tree) LongestPrefix(s string) (string, interface{}, bool)
func (t *Tree) Minimum() (string, interface{}, bool)
func (t *Tree) Maximum() (string, interface{}, bool)
func (t *Tree) Walk(fn WalkFn)
func (t *Tree) WalkPrefix(prefix string, fn WalkFn)
func (t *Tree) WalkPath(path string, fn WalkFn)
func (t *Tree) ToMap() map[string]interface{}
```

`New` returns an empty tree. `NewFromMap` inserts every map entry and returns
a tree containing one entry per key. A nil map is valid. `Len` counts stored
keys, including the empty string key when present.

`Insert` adds or replaces a key. It returns `(nil, false)` for a new key and
`(oldValue, true)` when replacing an existing key; replacing a key does not
change `Len`. `Get` and `Delete` perform exact key operations. They return the
stored value and `true` when the key exists, otherwise `(nil, false)`. Delete
removes the key and decrements the length. Empty strings are ordinary keys.

`DeletePrefix` removes every key beginning with the supplied prefix and
returns the number removed. An empty prefix removes the whole tree. A prefix
that matches no key returns zero. `LongestPrefix` returns the stored key with
the greatest length that is a prefix of the query, its value, and `true`; it
returns `("", nil, false)` when no stored key is a prefix. The empty key is a
valid longest-prefix result when it was inserted.

`Minimum` and `Maximum` return the lexicographically smallest and largest
stored keys, their values, and `true`. On an empty tree they return
`("", nil, false)`. Keys are compared by their Go string byte ordering.

`Walk` calls the callback once for each stored key in deterministic
lexicographic order. `WalkPrefix` visits only keys beginning with `prefix`, in
that same order. `WalkPath` visits stored keys on the path from the root to
`path`: a stored key is visited when it is a prefix of `path`, in increasing
key length/order along the path. A callback returning `true` stops that walk.
Callbacks may delete entries during a walk; the tree must remain valid.

`ToMap` returns a map containing every current key and its value. The returned
map need not have an observable iteration order. Tree methods must not share
mutable package-global state between instances.

## Implementation Notes

The evaluator calls the package through a newline-delimited JSON bridge. The
bridge constructs trees from bounded JSON entries and exposes deterministic
snapshots and mutation results; it does not serialize Go callbacks. Preserve
the public method signatures and return conventions so ordinary Go callers
can use callbacks directly. Diagnostics must go to stderr, not stdout, and a
normal request must produce exactly one structured JSON response.

Return errors are not part of this package's API. Do not panic for ordinary
bounded string keys or nil values. Keep the implementation pure Go and make
the module build with `GOWORK=off`, `GOPROXY=off`, `GOSUMDB=off`,
`GOTOOLCHAIN=local`, and `-mod=vendor`.

