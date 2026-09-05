# Build `better-sqlite3`

## Project Description

Create a complete, installable CommonJS npm package named `better-sqlite3`
from an empty workspace. Reproduce the documented database, statement,
transaction, SQLite error, and serialization behavior with Node 24's local
SQLite support. The contract is deliberately deterministic and does not
require the frozen upstream native addon.

## Natural Language Instruction

Implement four connected capabilities: a `Database` root export; prepared
statement binding and result modes; transaction, function, aggregate, pragma,
and serialization operations; and the exact `runScenario(name)` JSON adapter
listed below. Preserve nulls, Buffers, integers, row order, typed SQLite
errors, and idempotent close behavior. Use a local adapter available in the
locked runtime. Do not submit native `.node` files, `prebuilds/`,
`binding.gyp`, lifecycle downloads, workspaces, or a fake result-only package.

## Supports or Environment Configuration

- Node `24.19.0`, npm `11.17.0`, Linux amd64, glibc, and CommonJS modules.
- Package name and version are `better-sqlite3` and `13.0.3`; the package root
  must load with `require("better-sqlite3")`.
- Commit npm lockfile version 3. There are no candidate runtime dependencies;
  `npm ci --offline --ignore-scripts` must succeed.
- Agent, candidate, verifier, Oracle, controls, and runtime use
  `network_mode=no-network`. No AWS, GitHub, npm, DNS, SQLite download, or
  external service is permitted.

The authoritative package entry is CommonJS `require("better-sqlite3")`; Node
ESM interop may also use `import Database from "better-sqlite3"` without
changing the root export contract.

## Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
└── lib/
    ├── database.js
    ├── statement.js
    ├── transaction.js
    └── scenarios.js
```

`package.json` must point its CommonJS entry to `index.js`. The root exports
the default `Database` constructor, named `SqliteError`, and `runScenario`.

## API Usage Guide

`new Database(path = "", options = {})` opens `":memory:"`, an empty path, a
filesystem path, or a serialized `Buffer`. `options.readonly` is boolean.
Expose `name`, `memory`, `readonly`, `open`, and `inTransaction`. `close() =>
void` is idempotent. Invalid path/options types throw `TypeError`; operations
after close expose a `SqliteError` with the documented `SQLITE_MISUSE` code.

`exec(sql) => Database` executes SQL and returns the same database. `prepare(sql)
=> Statement` creates a statement. A statement supports `run(...params)`,
`get(...params)`, `all(...params)`, and `iterate(...params)`. Positional and
named parameters `?`, `@name`, `:name`, and `$name` are accepted. `run()`
returns `{changes, lastInsertRowid}`, `get()` returns one row or `undefined`,
`all()` returns rows, and `iterate()` yields rows in query order. `pluck()`,
`raw()`, `safeIntegers()`, and `expand()` return the statement for chaining;
`columns()` returns column metadata.

`transaction(fn) => callable` forwards arguments and return values. Its
`default`, `deferred`, `immediate`, and `exclusive` variants commit successful
calls and roll back thrown errors. Nested calls must preserve an outer change
when an inner failure is caught. `pragma(sql, {simple})` supports scalar and
row forms. `function(name, options, fn)` registers a deterministic scalar
function, and `aggregate(name, options)` registers an aggregate definition.
`serialize() => Buffer` and `deserialize(buffer) => void` support in-memory
databases. SQLite constraint failures expose codes such as
`SQLITE_CONSTRAINT_UNIQUE`.

```js
const Database = require("better-sqlite3");
const db = new Database(":memory:");
db.exec("CREATE TABLE t (id INTEGER PRIMARY KEY, name TEXT)");
db.prepare("INSERT INTO t VALUES (?, ?)").run(1, "Ada");
console.log(db.prepare("SELECT * FROM t").all());
db.close();
```

`runScenario(name) => object` supports exactly these deterministic names and
shapes: `basic` returns rows Ada/Linus, count 2, and `open: true`; `bindings`
returns positional 1, named 1, changes 2; `iteration` returns values [1,2,3];
`transactions` returns committed, rollback, and nested markers; `functions`
returns scalar 8 and aggregate 5; `pragma` returns foreignKeys 1 and numeric
cacheSize; `serialization` returns before/after `saved`; `errors` returns the
unique and misuse codes; `statementModes` returns pluck `"x"`, raw `[42,"x"]`,
and bigint type; `columns` returns names `["first","second"]` and count 2;
`readonly` returns true and `SQLITE_READONLY`; `apiShape` reports the required
exports and methods.

## Implementation Notes

Keep database handles local and close temporary files. The JSON scenario
adapter must call the real public API rather than hard-code expected output.
Use explicit type checks and preserve the runtime's SQL error codes. Results
must not depend on current time, random identifiers, process-global state, or
hash iteration order.

## Examples

```js
const Database = require("better-sqlite3");
const db = new Database(":memory:");
const tx = db.transaction((value) => db.prepare("INSERT INTO t VALUES (?)").run(value));
db.exec("CREATE TABLE t (value INTEGER)");
tx(1);
console.log(db.prepare("SELECT * FROM t").all());
```

```js
const result = require("better-sqlite3").runScenario("basic");
console.log(result.count, result.open);
```

## Error Handling and Boundary Conditions

- Empty path and `":memory:"` create local databases; malformed options throw
  `TypeError` before opening a handle.
- A unique-key violation must retain `SQLITE_CONSTRAINT_UNIQUE`, not become a
  generic JavaScript error.
- A transaction rolls back all work when its callback throws, while a caught
  nested failure does not erase earlier outer work.
- `serialize()`/`deserialize()` preserve stored values; readonly writes fail
  with `SQLITE_READONLY`, and repeated `close()` is harmless.
