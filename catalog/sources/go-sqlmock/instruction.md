# Recreate the deterministic core of go-sqlmock

## Project Description

Implement the Go module `github.com/DATA-DOG/go-sqlmock` as a pure-Go SQL
driver mock for deterministic unit tests. The package must let a caller create
a mock `*sql.DB`, declare expectations, execute database operations, and
inspect returned rows, results, and expectation errors without a real database.

The evaluator calls the package through a typed JSON bridge. Your repository is
empty at the start, so create the module, package, and all required source
files yourself. The implementation is judged by observable behavior, not by
matching the upstream file layout or private fields.

## Supports

- Linux/amd64 with Go `1.26.5`.
- A single root `go.mod` module whose path is exactly
  `github.com/DATA-DOG/go-sqlmock` and whose Go directive is `1.26.5`.
- The module requirement
  `github.com/kisielk/sqlstruct v0.0.0-20201105191214-5f3e10d3ab46` and its
  matching `go.sum` entries. The offline vendor closure supplied by the
  evaluator is verified against this lock.
- Offline builds with `GOWORK=off`, `GOPROXY=off`, `GOSUMDB=off`,
  `GOTOOLCHAIN=local`, `GOOS=linux`, `GOARCH=amd64`, and `CGO_ENABLED=0`.
- The standard library packages `database/sql`, `database/sql/driver`,
  `context`, `regexp`, `reflect`, `encoding/csv`, and `time` as needed.
- The frozen dependency closure is supplied by the build environment. Do not
  download modules, clone repositories, use cgo, use plugins, use `unsafe`,
  use `go generate`, or depend on a workspace or external `replace` directive.

The task contract deliberately excludes live external databases, callbacks,
goroutine scheduling guarantees, context cancellation timing, delayed
expectations, and the upstream example applications. These behaviors are not
needed for the deterministic bridge and cannot be made a stable JSON contract.

## API Usage Guide

Implement package `sqlmock` at the module root with these public APIs and
contracts.

### Creating a mock database

```go
func New(options ...SqlMockOption) (*sql.DB, Sqlmock, error)
func NewWithDSN(dsn string, options ...SqlMockOption) (*sql.DB, Sqlmock, error)
```

`New` creates an independently usable in-memory mock database and controller.
`NewWithDSN` uses the supplied non-empty data-source name and must reject a DSN
that is already registered. Both functions apply every option in order and
return an error when an option fails. Closing the returned database releases
its connection and unregisters its driver state.

`Sqlmock` exposes the expectation controller. Implement the deterministic
methods `ExpectQuery`, `ExpectExec`, `ExpectPrepare`, `ExpectBegin`,
`ExpectCommit`, `ExpectRollback`, `ExpectClose`, `ExpectationsWereMet`,
`MatchExpectationsInOrder`, `NewRows`, `NewRowsWithColumnDefinition`, and
`NewColumn`. Expectations are matched in declaration order by default; when
`MatchExpectationsInOrder(false)` is used, an eligible matching expectation may
be selected without relying on declaration order.

### Query and execution expectations

```go
func (m Sqlmock) ExpectQuery(expectedSQL string) *ExpectedQuery
func (m Sqlmock) ExpectExec(expectedSQL string) *ExpectedExec
func (m Sqlmock) ExpectPrepare(expectedSQL string) *ExpectedPrepare
func (e *ExpectedQuery) WithArgs(args ...driver.Value) *ExpectedQuery
func (e *ExpectedQuery) WithoutArgs() *ExpectedQuery
func (e *ExpectedQuery) WillReturnRows(rows ...*Rows) *ExpectedQuery
func (e *ExpectedQuery) WillReturnError(err error) *ExpectedQuery
func (e *ExpectedQuery) RowsWillBeClosed() *ExpectedQuery
func (e *ExpectedExec) WithArgs(args ...driver.Value) *ExpectedExec
func (e *ExpectedExec) WithoutArgs() *ExpectedExec
func (e *ExpectedExec) WillReturnResult(result driver.Result) *ExpectedExec
func (e *ExpectedExec) WillReturnError(err error) *ExpectedExec
```

Query and exec expectations compare SQL through the configured query matcher,
then compare the supplied driver values. `WithArgs` requires the same ordered
argument values; `WithoutArgs` rejects calls that contain arguments.
`WillReturnRows`, `WillReturnResult`, and `WillReturnError` determine the
observable result of a matching call. `RowsWillBeClosed` makes
`ExpectationsWereMet` report an error until the returned `*sql.Rows` is closed.
The builder methods return the same expectation pointer so calls can be
chained.

`ExpectedPrepare.ExpectQuery()` and `ExpectedPrepare.ExpectExec()` create a
child expectation for execution through the prepared statement. The prepared
statement expectation is fulfilled only when the statement is used as
declared; `WillBeClosed` requires the statement to be closed.

### Rows and results

```go
func NewRows(columns []string) *Rows
func NewRowsWithColumnDefinition(columns ...*Column) *Rows
func (r *Rows) AddRow(values ...driver.Value) *Rows
func (r *Rows) AddRows(values ...[]driver.Value) *Rows
func (r *Rows) FromCSVString(value string) *Rows
func (r *Rows) RowError(row int, err error) *Rows
func (r *Rows) CloseError(err error) *Rows
func NewResult(lastInsertID int64, rowsAffected int64) driver.Result
func NewErrorResult(err error) driver.Result
```

Rows preserve column order and row order. Each row must contain exactly one
value per column; an invalid row length is rejected without silently changing
the data. `FromCSVString` appends CSV records, converts the literal `NULL` to
SQL NULL, and reports malformed CSV through the query operation. `RowError`
causes iteration to end with the supplied error at the requested zero-based
row. `CloseError` causes closing the returned rows to report the supplied
error. `NewResult` returns the supplied values from `LastInsertId` and
`RowsAffected`; `NewErrorResult` returns the supplied error from both methods.

### Matchers, columns, and arguments

```go
type QueryMatcher interface {
    Match(expectedSQL, actualSQL string) error
}
type QueryMatcherFunc func(expectedSQL, actualSQL string) error
var QueryMatcherRegexp QueryMatcher
var QueryMatcherEqual QueryMatcher
func QueryMatcherOption(queryMatcher QueryMatcher) SqlMockOption
func AnyArg() Argument
func ValueConverterOption(converter driver.ValueConverter) SqlMockOption
func MonitorPingsOption(monitorPings bool) SqlMockOption
```

The regexp matcher strips and normalizes runs of whitespace before compiling
the expected expression and matching the actual SQL. The equal matcher strips
and normalizes whitespace on both sides and compares the resulting strings.
`QueryMatcherFunc.Match` delegates to the wrapped function. `AnyArg().Match`
accepts every valid `driver.Value`.

```go
func NewColumn(name string) *Column
func (c *Column) Name() string
func (c *Column) DbType() string
func (c *Column) OfType(dbType string, sampleValue interface{}) *Column
func (c *Column) Nullable(nullable bool) *Column
func (c *Column) WithLength(length int64) *Column
func (c *Column) WithPrecisionAndScale(precision, scale int64) *Column
func (c *Column) IsNullable() (bool, bool)
func (c *Column) Length() (int64, bool)
func (c *Column) PrecisionScale() (int64, int64, bool)
func (c *Column) ScanType() reflect.Type
```

Column builder methods return the same pointer. `OfType` records the database
type and derives the scan type from the supplied sample value. Metadata methods
return the configured value and a true availability flag when configured.

## Implementation Notes

Use the standard `database/sql/driver` contracts so ordinary `database/sql`
calls (`Query`, `Exec`, `Begin`, `Prepare`, `Commit`, `Rollback`, and row
iteration) observe the mock expectations. Keep each mock's mutable state
isolated and protect it when the API permits concurrent use. Expectation error
messages must be non-empty and stable enough for a caller to diagnose the
first unmatched operation; callers should rely on the error being non-nil,
not on private formatting.

The bridge only passes JSON scalars and copies row values before returning
them. Do not expose pointers, channels, callbacks, filesystem handles, live
connections, or aliased byte storage across the bridge. Do not write to
`/logs` or to verifier-owned files. The zero-argument and malformed-request
paths must return structured errors rather than panic or hang.
