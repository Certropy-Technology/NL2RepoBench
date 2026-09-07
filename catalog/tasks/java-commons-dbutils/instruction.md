## Project Description

Create an offline Java Maven project that recreates the bounded, public
Apache Commons DbUtils row-handler contract described below. The project is
for application developers who need to turn an existing JDBC `ResultSet`
into arrays, maps, scalar values, or an ordered list of values without
writing query-specific conversion code.

The implementation boundary is deliberately small. It covers the public
`BasicRowProcessor` row conversion methods and the first-row or column-list
handlers in `org.apache.commons.dbutils.handlers`. It does not require a
database connection, query execution, connection pooling, bean mapping,
asynchronous work, filesystem access, or network access.

The candidate must be a normal Maven project rooted at `workspace/`. Its
source package is `org.apache.commons.dbutils`, with handler classes below
`org.apache.commons.dbutils.handlers`. Keep the public names and generic
return shapes stable. Use only JDK modules at runtime, especially
`java.sql`, `java.util`, and `java.lang`.

The caller supplies a `ResultSet` that is already positioned or can be
advanced by a handler. A row processor reads the current row; a first-row
handler advances to the first row; a column-list handler advances through all
rows. SQL `NULL` must remain Java `null` in returned values.

The supplied source inventory identifies this bounded contract:

* `BasicRowProcessor.toArray(ResultSet)`
* `BasicRowProcessor.toMap(ResultSet)`
* `ArrayHandler.handle(ResultSet)`
* `MapHandler.handle(ResultSet)`
* `ScalarHandler.handle(ResultSet)`
* `ColumnListHandler.handle(ResultSet)`

Other upstream DbUtils APIs, including query runners, bean processors,
wrappers, connection behavior, and external/process paths, are outside this
task. Do not add them merely because they exist in the upstream project.

## Supports

### Natural Language Instruction

Implement the bounded Commons DbUtils API as a Java Maven project. Preserve
the exact package names, public signatures, checked exception behavior,
generic return types, row ordering, and empty-result behavior specified in
the API Usage Guide.

The project must support these capabilities:

1. Convert the current `ResultSet` row to an ordered `Object[]`.
2. Convert the current row to an insertion-ordered, case-insensitive map.
3. Read the first row through array, map, and scalar handlers.
4. Collect one indexed or named column from every row in source order.
5. Preserve SQL `NULL` values and propagate `SQLException` without replacing
   it with fabricated values.
6. Compile from the standard Maven layout with no runtime dependency beyond
   the Java platform.

### Runtime and Build Configuration

Use the following fixed environment:

```text
Language: Java
JDK: Temurin 21.0.12+8
Maven: 3.9.11
Platform: Linux amd64, glibc
Runtime dependencies: none beyond JDK modules
Network: unavailable during agent, candidate, verifier, Oracle, and control runs
```

The project may include a minimal `pom.xml` for Maven metadata, but the POM
must not add repositories, plugins, profiles, modules, custom extensions, or
runtime libraries to control verification. Do not depend on H2, Mockito,
Maven Central, a JDBC driver, a database server, DNS, or any external
service. `java.sql.ResultSet` and `java.sql.ResultSetMetaData` are the only
database-facing types needed by this contract.

### Project Directory Structure

Create the following public structure. The tree is rooted at `workspace/`.

```text
workspace/
├── pom.xml
└── src/
    └── main/
        └── java/
            └── org/
                └── apache/
                    └── commons/
                        └── dbutils/
                            ├── BasicRowProcessor.java
                            ├── ResultSetHandler.java
                            ├── RowProcessor.java
                            └── handlers/
                                ├── AbstractListHandler.java
                                ├── ArrayHandler.java
                                ├── ColumnListHandler.java
                                ├── MapHandler.java
                                └── ScalarHandler.java
```

The public contract exercised by this task is limited to the classes and
methods listed below. Supporting types may be minimal and must not expose
invented behavior. Do not add a CLI: this task has no command-line entry
point.

## API Usage Guide

### `org.apache.commons.dbutils.ResultSetHandler<T>`

This public interface represents a handler that consumes a JDBC result set.
The bounded contract uses its result shape as the common handler boundary.

```java
package org.apache.commons.dbutils;

import java.sql.ResultSet;
import java.sql.SQLException;

public interface ResultSetHandler<T> {
    T handle(ResultSet rs) throws SQLException;
}
```

`rs` must be a non-null result-set object supplied by the caller. The method
returns the handler-specific value and may advance the cursor according to
the concrete handler. It has no filesystem or network side effect. JDBC
failures from cursor movement, metadata, or value access are checked
`SQLException` failures and must cross the boundary unchanged. A normal
caller invokes `new MapHandler().handle(resultSet)`; an empty result is
interpreted by the concrete handler, not by this interface.

### `org.apache.commons.dbutils.BasicRowProcessor`

Construct the processor with its public no-argument constructor:

```java
BasicRowProcessor processor = new BasicRowProcessor();
```

The processor operates on the current row and must not call `ResultSet.next()`
for either conversion method. It is deterministic for a fixed result-set
state and has no mutable global state.

#### `toArray`

```java
public Object[] toArray(ResultSet rs) throws SQLException
```

`rs` must expose metadata and a current row. Read the column count and return
one value for each JDBC column in one-based column order. The returned array
has length equal to the metadata column count; element zero corresponds to
JDBC column 1. Preserve each `getObject` result, including Java `null` for
SQL `NULL`. Do not advance the cursor.

Normal example:

```java
Object[] row = new BasicRowProcessor().toArray(resultSet);
// A two-column row is represented as [firstValue, secondValue].
```

Edge example:

```java
Object[] emptyRow = new BasicRowProcessor().toArray(zeroColumnResultSet);
// A current row with zero columns produces an array of length zero.
```

If metadata access or a column read fails, propagate its `SQLException`.
Do not convert a failure into an empty array or a runtime-only exception.

#### `toMap`

```java
public Map<String, Object> toMap(ResultSet rs) throws SQLException
```

Read the current row without calling `next()`. Return a map whose entries
are inserted in JDBC column order. Resolve each key from the column label
when it is available, otherwise from the column name, and finally from the
one-based column number when neither name is usable. Preserve the original
key spelling during iteration and provide case-insensitive key semantics.
The map value is the corresponding `getObject` result, including `null`.

Normal example:

```java
Map<String, Object> row = new BasicRowProcessor().toMap(resultSet);
Object id = row.get("ID");
// "ID" and "id" address the same case-insensitive column key.
```

Edge example:

```java
Map<String, Object> row = new BasicRowProcessor().toMap(resultSetWithNull);
// A SQL NULL is retained as a map entry whose value is Java null.
```

Metadata, key-resolution, or value-access failures must propagate as
`SQLException`. Do not silently drop duplicate or null-valued columns.

### `org.apache.commons.dbutils.handlers.ArrayHandler`

Use the public no-argument constructor:

```java
public ArrayHandler()
```

The handler implements `ResultSetHandler<Object[]>` and exposes:

```java
public Object[] handle(ResultSet rs) throws SQLException
```

Call `next()` to inspect only the first row. If a row exists, convert that
row using the same ordered array behavior as `BasicRowProcessor.toArray`.
For an empty result set, return an empty `Object[]`. Do not inspect later
rows. A cursor failure, metadata failure, or value failure propagates as
`SQLException`.

Normal example:

```java
Object[] first = new ArrayHandler().handle(resultSet);
// Only the first row is returned, even when more rows are available.
```

Edge example:

```java
Object[] none = new ArrayHandler().handle(emptyResultSet);
// `none.length` is zero and no placeholder value is fabricated.
```

### `org.apache.commons.dbutils.handlers.MapHandler`

Use the public no-argument constructor:

```java
public MapHandler()
```

The handler exposes:

```java
public Map<String, Object> handle(ResultSet rs) throws SQLException
```

Advance to the first row only. Convert it with the same ordered,
case-insensitive map behavior as `BasicRowProcessor.toMap`. Return `null`
when `next()` reports that there is no row. Preserve SQL `NULL` values in a
present row. Cursor, metadata, and value failures remain `SQLException`.

Normal example:

```java
Map<String, Object> first = new MapHandler().handle(resultSet);
Object name = first.get("name");
```

Edge example:

```java
Map<String, Object> none = new MapHandler().handle(emptyResultSet);
// `none` is null for an empty result set.
```

### `org.apache.commons.dbutils.handlers.ScalarHandler<T>`

The generic scalar handler has these public constructors:

```java
public ScalarHandler()
public ScalarHandler(int columnIndex)
public ScalarHandler(String columnName)
```

Its public operation is:

```java
public T handle(ResultSet rs) throws SQLException
```

The no-argument form selects one-based column 1. The integer form selects
the requested one-based JDBC column index. The string form selects the
named column using the result-set column-name contract. Each form advances
to the first row only and returns that cell, including Java `null` for SQL
`NULL`. If there is no row, return `null`. Invalid indexes, missing names,
cursor movement failures, and value-access failures follow JDBC behavior and
are reported as `SQLException`; do not select a different column silently.

Normal example:

```java
String firstName = new ScalarHandler<String>("name").handle(resultSet);
Integer firstId = new ScalarHandler<Integer>(1).handle(resultSet);
```

Edge example:

```java
Object absent = new ScalarHandler<Object>().handle(emptyResultSet);
// `absent` is null when there is no first row.
```

### `org.apache.commons.dbutils.handlers.ColumnListHandler<T>`

The generic column-list handler has these public constructors:

```java
public ColumnListHandler()
public ColumnListHandler(int columnIndex)
public ColumnListHandler(String columnName)
```

Its public operation is:

```java
public List<T> handle(ResultSet rs) throws SQLException
```

The no-argument form selects one-based column 1. The integer form selects
the requested index, and the string form selects the requested column name.
Advance through every row exactly once, append one selected value per row,
and preserve source-row order. Preserve SQL `NULL` as a list element whose
value is Java `null`; do not filter or compact the list. Return an empty list
when there are no rows. Invalid indexes, missing names, cursor failures, and
value failures must follow the checked `SQLException` contract.

Normal example:

```java
List<String> names = new ColumnListHandler<String>("name").handle(resultSet);
// Names appear in the same order as their rows.
```

Edge example:

```java
List<Object> values = new ColumnListHandler<Object>(2).handle(resultSetWithNull);
// A middle SQL NULL remains a middle Java null list element.
```

### Import and Usage Boundary

Use these imports in client code:

```java
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;
import java.util.Map;
import org.apache.commons.dbutils.BasicRowProcessor;
import org.apache.commons.dbutils.ResultSetHandler;
import org.apache.commons.dbutils.RowProcessor;
import org.apache.commons.dbutils.handlers.ArrayHandler;
import org.apache.commons.dbutils.handlers.ColumnListHandler;
import org.apache.commons.dbutils.handlers.MapHandler;
import org.apache.commons.dbutils.handlers.ScalarHandler;
```

`RowProcessor` and `AbstractListHandler` are supporting public types in the
source layout, but no additional methods on them are confidently bindable
to this bounded task contract. Do not invent or implement extra API surface
for them solely from their names. The six operations documented above are
the required behavior.

## Implementation Notes

Keep all implementation files under the Maven source tree shown above and
keep package declarations synchronized with their paths. The candidate POM
is metadata only; it must not control how the contract is verified.

The implementation must satisfy these cross-module constraints:

1. `ArrayHandler` and `MapHandler` must use the same row ordering and value
   conversion semantics as `BasicRowProcessor`.
2. `ScalarHandler` and `ColumnListHandler` must use one-based JDBC indexes,
   named-column access, and the same SQL `NULL` preservation rule.
3. First-row handlers stop after the first row; `ColumnListHandler` consumes
   all rows. Do not share cursor state across handler instances.
4. Returned arrays, maps, and lists must be deterministic for a fixed
   `ResultSet` sequence. Do not use unordered iteration to determine output
   order.
5. Propagate checked `SQLException` from `ResultSet.next()`, metadata, and
   value access. Do not catch it merely to return a default value.
6. Do not read environment variables, write files, open sockets, load a
   database driver, or invoke an external process.

Small verifiable examples include:

* A two-column current row becomes an array with values in columns 1 then 2.
* A first-row map retains its column insertion order and accepts a lookup
  using a different key case.
* An empty result gives an empty array, `null` map, `null` scalar, and empty
  column list according to the selected handler.
* A three-row column list retains a SQL `NULL` in its original middle
  position rather than dropping it.

Do not copy a reference implementation or encode a hidden test fixture in
the project. Implement the public behavior using ordinary Java types and
the JDK JDBC interfaces. Keep behavior stable across repeated calls with
equivalent result-set inputs, and preserve the exact generic shapes
`Object[]`, `Map<String,Object>`, `T`, and `List<T>` described above.

There is no CLI, web service, database schema, asynchronous API, or command
to document. A normal build is an offline Maven validation/build using JDK
21. Runtime dependency closure must remain empty. Any unsupported upstream
feature should remain absent rather than being represented by a guessed
signature or a no-op placeholder.
