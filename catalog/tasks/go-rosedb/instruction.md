# Project Description

Implement the pure-Go `github.com/rosedblabs/rosedb/v2` key/value storage
engine as one Go module at the repository root. RoseDB uses a log-structured
WAL and an in-memory ordered index. The implementation must preserve the
observable behavior of the frozen upstream API described below, including
durable reopen, atomic batches, ordered iteration, expiration, and key-watch
events.

# Supports

- Linux/amd64 with Go `1.26.5` and `CGO_ENABLED=0`.
- A root `go.mod` whose module path is exactly
  `github.com/rosedblabs/rosedb/v2`, a matching `go.sum`, and no workspace or
  external `replace` directive.
- Offline builds with `GOWORK=off GOPROXY=off GOSUMDB=off
  GOTOOLCHAIN=local`, using `go test -mod=vendor ./...`.
- Filesystem-backed operation under a caller-provided directory. Do not use
  network services, cgo, plugins, or unbounded background work.

# Natural Language Instruction

Create the filesystem-backed `github.com/rosedblabs/rosedb/v2` module from an
empty workspace. Implement configuration, durable single-key operations,
atomic batches, expiration, ordered scans, iterators, and watch events exactly
as described below.

# Project Directory Structure

```text
workspace/
├── go.mod
├── go.sum
├── vendor/modules.txt
├── db.go
├── options.go
├── batch.go
├── iterator.go
├── item.go
└── watcher.go
```

Expose the root package as `rosedb "github.com/rosedblabs/rosedb/v2"`.
Persistence uses only the caller-provided directory; evaluation-only files are
not part of the generated module.

# Examples

```go
db, err := rosedb.Open(rosedb.DefaultOptions("/tmp/rose")); defer db.Close()
err = db.Put([]byte("name"), []byte("Ada"))
```

```go
batch := db.NewBatch(rosedb.DefaultBatchOptions()); _ = batch.Put([]byte("k"), []byte("v")); _ = batch.Commit()
```

# Error Handling and Boundary Conditions

Preserve empty-key and missing-key errors, close/reopen durability, pending
batch visibility, rollback, TTL expiry/persistence, iterator closure, ordered
half-open scans, watch delivery bounds, and all exported error identities.
Never contact a network service; filesystem paths remain caller-controlled.

```go
import rosedb "github.com/rosedblabs/rosedb/v2"
```

# API Usage Guide

Import the root package as `rosedb "github.com/rosedblabs/rosedb/v2"`.

## Opening and single-key operations

Preserve these public declarations and their input/output contracts:

```go
type Options struct {
    DirPath string
    SegmentSize int64
    Sync bool
    BytesPerSync uint32
    WatchQueueSize uint64
    AutoMergeCronExpr string
}

var DefaultOptions Options

func Open(options Options) (*DB, error)
func (db *DB) Close() error
func (db *DB) Sync() error
func (db *DB) Put(key, value []byte) error
func (db *DB) Get(key []byte) ([]byte, error)
func (db *DB) Delete(key []byte) error
func (db *DB) Exist(key []byte) (bool, error)
func (db *DB) Stat() *Stat
```

`Open` creates a missing `DirPath`, reconstructs the index from existing WAL
files, and rejects a directory already held by another process. `Put` replaces
the value for an existing non-empty key. `Get` returns a copy-equivalent byte
slice and `ErrKeyNotFound` for an absent, deleted, or expired key. `Delete` is
successful for a non-empty key and makes subsequent `Get` absent. Empty keys
return `ErrKeyIsEmpty`. `Close` releases database resources and the directory
lock; after close, operations report `ErrDBClosed`. `Stat` reports `KeysNum`
and the current directory `DiskSize`.

The exported sentinel errors include `ErrKeyIsEmpty`, `ErrKeyNotFound`,
`ErrDatabaseIsUsing`, `ErrReadOnlyBatch`, `ErrBatchCommitted`,
`ErrBatchRollbacked`, `ErrDBClosed`, `ErrMergeRunning`, and
`ErrWatchDisabled`. Preserve their non-nil/error identity behavior.

## TTL and expiration

```go
func (db *DB) PutWithTTL(key, value []byte, ttl time.Duration) error
func (db *DB) Expire(key []byte, ttl time.Duration) error
func (db *DB) TTL(key []byte) (time.Duration, error)
func (db *DB) Persist(key []byte) error
func (db *DB) DeleteExpiredKeys(timeout time.Duration) error
```

Positive TTLs expire keys after the duration. `TTL` returns the remaining
duration for an expiring key, `-1` for a persistent key, and
`ErrKeyNotFound` for an absent or expired key. `Persist` removes expiration and
returns `ErrKeyNotFound` when the key is absent.

## Batches

```go
type BatchOptions struct { Sync bool; ReadOnly bool }
var DefaultBatchOptions BatchOptions
func (db *DB) NewBatch(options BatchOptions) *Batch
func (b *Batch) Put(key, value []byte) error
func (b *Batch) PutWithTTL(key, value []byte, ttl time.Duration) error
func (b *Batch) Get(key []byte) ([]byte, error)
func (b *Batch) Delete(key []byte) error
func (b *Batch) Exist(key []byte) (bool, error)
func (b *Batch) Expire(key []byte, ttl time.Duration) error
func (b *Batch) TTL(key []byte) (time.Duration, error)
func (b *Batch) Persist(key []byte) error
func (b *Batch) Commit() error
func (b *Batch) Rollback() error
```

A writable batch stages changes until `Commit`; `Rollback` discards them.
Pending reads see pending writes. A read-only batch permits reads only. A batch
must be committed or rolled back before the database is used by another
operation. Commit persists all staged records as one atomic batch and exposes
watch events with one batch id.

## Ordered traversal and watch

```go
type IteratorOptions struct { Prefix []byte; Reverse bool; ContinueOnError bool }
var DefaultIteratorOptions IteratorOptions
type Item struct { Key []byte; Value []byte }
func (db *DB) NewIterator(opts IteratorOptions) *Iterator
func (it *Iterator) Rewind()
func (it *Iterator) Seek(key []byte)
func (it *Iterator) Next()
func (it *Iterator) Valid() bool
func (it *Iterator) Item() *Item
func (it *Iterator) Close()
func (it *Iterator) Err() error
```

Iterators traverse live, non-expired entries in bytewise key order. `Reverse`
traverses descending, `Prefix` filters keys, `Seek` positions at the requested
key, and `Item` is stable until movement. `Close` makes the iterator invalid.

The callback scans are also public:

```go
func (db *DB) Ascend(fn func(k, v []byte) (bool, error))
func (db *DB) AscendRange(startKey, endKey []byte, fn func(k, v []byte) (bool, error))
func (db *DB) AscendGreaterOrEqual(key []byte, fn func(k, v []byte) (bool, error))
func (db *DB) Descend(fn func(k, v []byte) (bool, error))
func (db *DB) DescendRange(startKey, endKey []byte, fn func(k, v []byte) (bool, error))
func (db *DB) DescendLessOrEqual(key []byte, fn func(k, v []byte) (bool, error))
func (db *DB) AscendKeys(pattern []byte, filterExpired bool, fn func(k []byte) (bool, error)) error
func (db *DB) AscendKeysRange(startKey, endKey, pattern []byte, filterExpired bool, fn func(k []byte) (bool, error)) error
func (db *DB) DescendKeys(pattern []byte, filterExpired bool, fn func(k []byte) (bool, error)) error
func (db *DB) DescendKeysRange(startKey, endKey, pattern []byte, filterExpired bool, fn func(k []byte) (bool, error)) error
```

Scan callbacks stop when they return `false`; key scans optionally filter
expired records and treat `pattern` as a Go regular expression.

```go
type Event struct { Action WatchActionType; Key []byte; Value []byte; BatchId uint64 }
const ( WatchActionPut WatchActionType = iota; WatchActionDelete )
func (db *DB) Watch() (<-chan *Event, error)
func NewWatcher(capacity uint64) *Watcher
func (w *Watcher) Close()
```

Set `Options.WatchQueueSize` above zero to enable `Watch`. A successful put or
delete emits the matching action and key; a delete has an empty value. Calling
`Watch` while disabled returns `ErrWatchDisabled`.

# Implementation Notes

Keep the root package importable without an application main package. Use the
declared module dependencies through the vendored offline closure and do not
add a `replace` directive. The evaluator uses a private typed bridge to run
bounded filesystem scenarios in a candidate-owned subprocess; callback and
channel behavior is exercised inside that bridge. Do not hard-code evaluator
outputs, add a second module, or expose private test material.
