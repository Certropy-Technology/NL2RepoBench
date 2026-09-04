# go-buntdb authoring audit: blocked

## Project Description

`go-buntdb` is the pure-Go `github.com/tidwall/buntdb` embedded key-value
database at immutable revision `0dbc8c18459aed4e4179bccbe0322bbd6019733f`.
This source-local record is an authoring audit, not a production Harbor task.
No generated runtime, private test bundle, Oracle bundle, dependency cache, or
shared index is included.

## Supports

The frozen repository contains one package, one implementation file, one Go
test file, and a `go.mod` requiring nine `tidwall` modules. The intended
production target would be Linux/amd64 with Go `1.26.5`, `CGO_ENABLED=0`, and
no run-time network access. The source revision and MIT license were fetched
and hashed, but the required private module closure is not available in this
task-local authoring lane.

## API Usage Guide

The public surface includes `Open(path string) (*DB, error)`, `DB.Close`,
`DB.Save`, `DB.Load`, `DB.CreateIndex`, `DB.CreateSpatialIndex`,
`DB.DropIndex`, `DB.Indexes`, `DB.ReadConfig`, `DB.SetConfig`, `DB.View`,
`DB.Update`, and transaction methods for `Set`, `Get`, `Delete`, `TTL`,
`Len`, iteration, index range queries, spatial queries, and commit/rollback.
It also includes `Match`, `Rect`, `Point`, `IndexRect`, `IndexString`,
`IndexBinary`, `IndexInt`, `IndexUint`, `IndexFloat`, `IndexJSON`,
`IndexJSONCaseSensitive`, and `Desc`.

The API has mutable transactions, snapshot iteration, persistence and replay,
TTL expiration, expiration callbacks, text/JSON/numeric/spatial indexes, and
filesystem behavior. A faithful production task needs a bounded child-side
adapter that keeps those effects separate from the trusted verifier.

## Implementation Notes

The source is not copied into this public projection. Its archive digest is
`sha256:739a637fe699cfbe0a08e8a0ce8d7afed3ae76efe598ba4b3096f36fcc7008eb` and
the MIT `LICENSE` digest is
`sha256:be83ad53208d03a9fe08c7fac231cabf79422989ef5706bff217bd35104ebf07`.

The frozen source has 39 Go test functions in `buntdb_test.go`, covering basic
transactions, save/load, persistence, expiration, many index modes, spatial
queries, callbacks, and close/error behavior. The clean offline dependency
probe below exits before collection because `GOPROXY=off` cannot resolve the
missing modules. No Oracle, controls, Harbor collection, or reward is claimed.

## Evidence and blocker

The source freeze log records the exact commit, archive, and license hashes.
The dependency probe log records the real no-network command and its exit code.
The API and test inventories are static records tied to the frozen checkout.

Primary failure class: `environment`, with a secondary `verifier` blocker.

Next steps:

1. Materialize and hash-lock all nine direct and indirect Go modules in the
   private CAS, without placing them in the public projection.
2. Define a bounded typed child adapter for deterministic in-memory CRUD,
   transaction rollback, lexical/index scans, TTL, and controlled save/load.
3. Decide whether persistence, expiration callbacks, JSON/spatial indexes, and
   concurrent workloads are in scope; exclude unsupported behavior explicitly.
4. Add public-behavior tests and a fixed collection denominator in a private
   verifier, then compile the final bundle and run Oracle plus all controls.

Until those artifacts and decisions exist, this task remains blocked and must
not receive a `catalog/tasks/go-buntdb` runtime.
