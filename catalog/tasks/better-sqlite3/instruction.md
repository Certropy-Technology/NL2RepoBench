# Build `better-sqlite3`

Create a complete, installable npm package named `better-sqlite3` from an empty
workspace. The package must be CommonJS-compatible and expose the default
`Database` constructor plus the named `SqliteError` export from its package root.

## Scope and deterministic adaptation

The frozen upstream project is a native SQLite addon. This task runs with no
network and does not permit candidate native binaries, `node-gyp`, lifecycle
builds, or downloaded SQLite sources. Implement the required behavior using the
Node 24 standard-library `node:sqlite` API or another pure-JavaScript adapter
available in the locked image. Do not submit `.node` files, `prebuilds/`,
`binding.gyp`, workspaces, registry settings, or install scripts.

For verifier-safe JSON calls, also export `runScenario(name)` from the package
root. It must execute the package API in a fresh in-memory database and return a
JSON-serializable value for each required scenario name below. This is a bounded
adapter for testing the class API in a separate candidate process; it is not a
replacement for the class API.

## Required package contract

Use a committed npm v3 `package-lock.json`. `npm ci --offline --ignore-scripts`
must succeed with the package manager preloaded by the task environment. The
package must not require runtime dependencies.

`new Database(path = "")` opens a database. `":memory:"`, an empty string, and a
filesystem path are supported. The instance exposes `name`, `memory`, `readonly`,
`open`, and `inTransaction`; `close()` closes the connection and is idempotent.
Invalid path or option types must throw `TypeError`. `exec(sql)` executes SQL and
returns the database. `prepare(sql)` returns a statement.

A statement supports `run(...params)`, `get(...params)`, `all(...params)`, and
`iterate(...params)`. Positional values and named objects for `?`, `@name`,
`:name`, and `$name` parameters must work. `run()` returns `{ changes,
lastInsertRowid }`; `get()` returns one row or `undefined`; `all()` returns all
rows; `iterate()` yields rows in query order. `pluck()`, `raw()`,
`safeIntegers()`, and `expand()` return the statement for chaining and affect
the corresponding result shape. `columns()` returns column metadata.

`transaction(fn)` returns a callable transaction wrapper with `default`,
`deferred`, `immediate`, and `exclusive` variants. Arguments and return values
are forwarded. Successful calls commit; thrown errors roll back. Nested wrappers
must use savepoint-like behavior so an inner failure can be caught without
discarding earlier outer work.

Implement `pragma(sql, { simple })`, `function(name, options, fn)`, and
`aggregate(name, options)` for deterministic scalar and aggregate SQL calls.
Implement `serialize()` and `deserialize(buffer)` for an in-memory database.
SQLite errors must expose a useful `code` such as `SQLITE_CONSTRAINT_UNIQUE`.

## Required JSON scenarios

`runScenario` must support exactly these names and return the described shape:

- `basic`: create a table, insert two rows, and return `{ rows, count, open }`.
- `bindings`: exercise positional and named parameters and return `{ positional,
  named, changes }`.
- `iteration`: return `{ values }` from an ordered iterator.
- `transactions`: return `{ committed, rolledBack, nested }` after commit,
  rollback, and a caught nested transaction failure.
- `functions`: return `{ scalar, aggregate }` from registered SQL functions.
- `pragma`: return `{ foreignKeys, cacheSizeType }`.
- `serialization`: return `{ before, after }` after serializing and reopening.
- `errors`: return `{ constraintCode, closedError }` for a unique constraint and
  an operation after close.
- `statementModes`: return `{ pluck, raw, safeIntegerType }`.
- `columns`: return `{ names, count }` for statement column metadata.
- `readonly`: return `{ readonly, writeCode }` for a readonly file connection.
- `apiShape`: return `{ hasDatabase, hasSqliteError, methods }`.

Keep results deterministic: do not use current time, random values, external
files, network access, or process-global mutable state. The hidden verifier uses
one leaf test per scenario and derives the fixed denominator from this list.

## Implementation notes

Keep the implementation in ordinary source files under the package root. The
root export must work with `require("better-sqlite3")`. Preserve null values,
Buffer values, integer values, and row ordering. Use explicit validation and
close database handles in scenario helpers. Do not copy the upstream source or
tests into the candidate workspace, and do not expose verifier assets.
