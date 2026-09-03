# Recreate a bounded Badger key-value database API

## Project Description

Create the pure-Go `github.com/dgraph-io/badger/v4` package at repository
root. Badger is an embedded transactional key-value database. This task uses a
small deterministic bridge to exercise the core in-memory database workflow:
open an in-memory database, commit and read values, roll back a callback, delete
keys, attach user metadata, and iterate keys in lexical order.

The repository is evaluated from an empty workspace. Implement the package and
module metadata; do not copy the reference implementation or add a dependency
on a network service.

## Supports

- Linux/amd64 with Go `1.26.5`, `CGO_ENABLED=0`, and one root Go module.
- Module path `github.com/dgraph-io/badger/v4`, an exact `go 1.26.5` directive,
  `go.sum`, and a complete `vendor/modules.txt` closure.
- Offline commands with `GOOS=linux GOARCH=amd64 CGO_ENABLED=0 GOWORK=off
  GOPROXY=off GOSUMDB=off GOTOOLCHAIN=local`.
- The public bridge imports only `github.com/dgraph-io/badger/v4`. Its request
  payloads are bounded: at most 64 records, keys and values up to 4096 bytes,
  and prefixes up to 4096 bytes.

## API Usage Guide

Implement the following public API at import path
`github.com/dgraph-io/badger/v4`.

### Options and database lifecycle

```go
type Options struct { /* public configuration fields, private test fields */ }
func DefaultOptions(path string) Options
func (opt Options) WithInMemory(value bool) Options
func (opt Options) WithLogger(logger Logger) Options
func Open(opt Options) (*DB, error)
func (db *DB) Close() error
func (db *DB) IsClosed() bool
```

`DefaultOptions("").WithInMemory(true)` must produce a database that does not
require a filesystem. `WithLogger(nil)` disables logging for an embedding
application. `Open` returns a usable database or an error and must not leave a
partially usable value after failure. `Close` is idempotent, and operations on a
closed database return an error rather than silently succeeding.

### Transactions

```go
type Txn struct { /* private state */ }
func (db *DB) NewTransaction(update bool) *Txn
func (db *DB) View(fn func(txn *Txn) error) error
func (db *DB) Update(fn func(txn *Txn) error) error
func (txn *Txn) Set(key, value []byte) error
func (txn *Txn) SetEntry(entry *Entry) error
func (txn *Txn) Get(key []byte) (*Item, error)
func (txn *Txn) Delete(key []byte) error
func (txn *Txn) Commit() error
func (txn *Txn) Discard()
```

Read-only transactions may call `Get` and iterate but cannot call `Set` or
`Delete`. An update transaction sees its own writes. `Update` commits only when
its callback returns nil; an error from the callback leaves its writes
uncommitted. `View` always discards its read-only transaction. Callers must
discard manually created transactions, including after a failed operation.
`Get` returns `ErrKeyNotFound` for an absent or deleted key. Empty keys return
`ErrEmptyKey`; invalid operations return the corresponding exported sentinel
error, including `ErrReadOnlyTxn`, `ErrDiscardedTxn`, and `ErrDBClosed`.

### Entries and items

```go
type Entry struct {
    Key []byte
    Value []byte
    UserMeta byte
    ExpiresAt uint64
}
func NewEntry(key, value []byte) *Entry
func (entry *Entry) WithMeta(meta byte) *Entry

type Item struct { /* private representation */ }
func (item *Item) Key() []byte
func (item *Item) KeyCopy(dst []byte) []byte
func (item *Item) Value(fn func([]byte) error) error
func (item *Item) ValueCopy(dst []byte) ([]byte, error)
func (item *Item) Version() uint64
func (item *Item) UserMeta() byte
func (item *Item) KeySize() int64
func (item *Item) ValueSize() int64
func (item *Item) IsDeletedOrExpired() bool
```

`NewEntry` creates a settable key/value entry. `WithMeta` stores one user
metadata byte and returns the same entry for chaining. `Item.Key` and the value
passed to `Value` are transaction-scoped; use `KeyCopy` and `ValueCopy` when a
copy must outlive the current item. `Version` is a positive commit timestamp
for committed data. `Value` calls its callback once with the value and
propagates the callback error; `ValueCopy` returns an independent copy.

### Iteration

```go
type IteratorOptions struct {
    PrefetchSize int
    PrefetchValues bool
    Reverse bool
    AllVersions bool
    InternalAccess bool
    Prefix []byte
    SinceTs uint64
}
var DefaultIteratorOptions IteratorOptions
func (txn *Txn) NewIterator(opt IteratorOptions) *Iterator
func (it *Iterator) Rewind()
func (it *Iterator) Seek(key []byte)
func (it *Iterator) Next()
func (it *Iterator) Valid() bool
func (it *Iterator) ValidForPrefix(prefix []byte) bool
func (it *Iterator) Item() *Item
func (it *Iterator) Close()
```

An iterator returns keys in lexicographic order, or reverse lexicographic order
when `Reverse` is true. `Prefix` restricts results to that prefix. Call
`Rewind`, check `Valid`, read `Item`, then call `Next`; close the iterator before
discarding its transaction. Iteration is over a transaction snapshot, and the
iterator's current item must not be retained after advancing.

### Error values

Export the sentinel errors needed by the contracts: `ErrKeyNotFound`,
`ErrReadOnlyTxn`, `ErrDiscardedTxn`, `ErrEmptyKey`, and `ErrDBClosed`. Their
errors must be discoverable with `errors.Is` when wrapped.

## Implementation Notes

Keep the implementation pure Go and deterministic for the bridge operations.
The bridge deliberately uses `WithInMemory(true)` and never tests persistence,
value-log GC, TTL expiration, encryption, streams, backup/restore, managed
transactions, callbacks that retain items, or concurrent long-running
workloads. Those APIs may remain outside the supported slice, but the package
must compile as one module and must not use cgo, plugins, generated code, or
network access.

Do not hard-code the bridge's fixtures or return verifier-owned reports from the
package. Preserve byte values exactly, copy data where the API promises a copy,
maintain transaction isolation, and avoid goroutine leaks after `Close`.
