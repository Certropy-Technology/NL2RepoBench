# Introduction and Goals of the Commons DbUtils Project

Apache Commons DbUtils is a Java library that reduces boilerplate when a
`java.sql.ResultSet` is converted into application values. This task focuses
on a small, deterministic handler slice: row-to-array and row-to-map
conversion, first-row handlers, scalar column access, and collection of one
column across rows. The implementation must use the public DbUtils packages
and work without a database, network connection, or third-party runtime
dependency.

## Natural Language Instruction (Prompt)

Please create a Java Maven project named Commons DbUtils that implements the
following public behavior:

1. Convert the current `ResultSet` row to an ordered `Object[]` with
   `BasicRowProcessor.toArray(ResultSet)`.
2. Convert the current row to an insertion-ordered, case-insensitive map with
   `BasicRowProcessor.toMap(ResultSet)`. Use the column label when available,
   then the column name, and finally the one-based column number as the key.
3. Implement `ArrayHandler`, `MapHandler`, and `ScalarHandler` first-row
   behavior, including their documented empty-result values.
4. Implement `ColumnListHandler` for an indexed column and a named column,
   preserving row order and SQL NULL values.
5. Preserve `SQLException` propagation and the exact public generic return
   shapes.
6. Keep source files in the normal Maven layout under `src/main/java` and do
   not add runtime dependencies, plugins, repositories, profiles, modules, or
   custom build extensions to control verification.

## Environment Configuration

### Core Dependency Library Versions

```Plain
Temurin JDK 21.0.12+8       # Java compilation and execution
Maven 3.9.11                # Project metadata and offline smoke only
Linux amd64                 # Fixed execution platform
Runtime dependencies: none  # java.sql and java.util are JDK modules
Network access: unavailable # Agent, candidate, verifier, and controls
```

The candidate `pom.xml` is metadata only. The verifier compiles the public
contract in a separate JVM and does not trust candidate Maven configuration.

## Commons DbUtils Project Architecture

### Project Directory Structure

```Plain
workspace/
├── pom.xml
└── src
    └── main
        └── java
            └── org
                └── apache
                    └── commons
                        └── dbutils
                            ├── BasicRowProcessor.java
                            ├── ResultSetHandler.java
                            ├── RowProcessor.java
                            └── handlers
                                ├── AbstractListHandler.java
                                ├── ArrayHandler.java
                                ├── ColumnListHandler.java
                                ├── MapHandler.java
                                └── ScalarHandler.java
```

The verifier supplies a controlled `ResultSet` adapter. Do not implement a
real database driver, connect to H2, or use external services.

## API Usage Guide

### Core APIs

#### 1. Module Import

```java
import java.sql.ResultSet;
import org.apache.commons.dbutils.BasicRowProcessor;
import org.apache.commons.dbutils.handlers.ArrayHandler;
import org.apache.commons.dbutils.handlers.ColumnListHandler;
import org.apache.commons.dbutils.handlers.MapHandler;
import org.apache.commons.dbutils.handlers.ScalarHandler;
```

#### 2. BasicRowProcessor.toArray() - Convert the Current Row

```java
Object[] values = new BasicRowProcessor().toArray(resultSet);
```

Signature:

```java
Object[] toArray(ResultSet resultSet) throws SQLException
```

Read the metadata column count and return values in one-based JDBC column
order. The method reads the current row; it does not call `next()`.

#### 3. BasicRowProcessor.toMap() - Convert the Current Row to a Map

```java
Map<String, Object> values = new BasicRowProcessor().toMap(resultSet);
```

Signature:

```java
Map<String, Object> toMap(ResultSet resultSet) throws SQLException
```

The returned map preserves column insertion order. Lookup is case-insensitive
while the original column label spelling remains the iteration key.

#### 4. ArrayHandler - Read the First Row

```java
Object[] values = new ArrayHandler().handle(resultSet);
```

Signature:

```java
Object[] handle(ResultSet resultSet) throws SQLException
```

The handler calls `next()` once. It returns the current row as an array, or an
empty array when there are no rows.

#### 5. MapHandler - Read the First Row as a Map

```java
Map<String, Object> values = new MapHandler().handle(resultSet);
```

Signature:

```java
Map<String, Object> handle(ResultSet resultSet) throws SQLException
```

The handler returns the first row as a map, or `null` for an empty result set.

#### 6. ScalarHandler - Read One Value from the First Row

```java
Object first = new ScalarHandler<>().handle(resultSet);
Object named = new ScalarHandler<>("name").handle(resultSet);
Object indexed = new ScalarHandler<>(2).handle(resultSet);
```

Signatures:

```java
ScalarHandler()
ScalarHandler(int columnIndex)
ScalarHandler(String columnName)
T handle(ResultSet resultSet) throws SQLException
```

The default selects column 1. An indexed or named handler selects that column
from the first row and returns `null` when the result set is empty.

#### 7. ColumnListHandler - Collect One Column

```java
List<Object> values = new ColumnListHandler<>(2).handle(resultSet);
List<Object> named = new ColumnListHandler<>("name").handle(resultSet);
```

Signatures:

```java
ColumnListHandler()
ColumnListHandler(int columnIndex)
ColumnListHandler(String columnName)
List<T> handle(ResultSet resultSet) throws SQLException
```

The default selects column 1. The result contains one value per row in source
order, including `null` values. An empty result set produces an empty list.

### Actual Usage Modes

#### Basic Row Processing

```java
ResultSet resultSet = obtainResultSetFromTheCaller();
Object[] row = new BasicRowProcessor().toArray(resultSet);
Map<String, Object> map = new BasicRowProcessor().toMap(resultSet);
```

#### First-Row Handlers

```java
Object[] firstRow = new ArrayHandler().handle(resultSet);
Map<String, Object> firstMap = new MapHandler().handle(resultSet);
Object firstValue = new ScalarHandler<>("name").handle(resultSet);
```

#### All-Row Column Collection

```java
List<Object> names = new ColumnListHandler<>("name").handle(resultSet);
```

### Supported Function Types

The supported functions are deterministic `ResultSet` row conversion, first
row extraction, indexed or named scalar access, and indexed or named column
collection. Query execution, JDBC connection management, bean mapping,
asynchronous runners, database drivers, and wrapper classes are outside this
contract.

### Error Handling

Propagate `SQLException` from metadata, cursor movement, and value access.
Preserve SQL NULL as Java `null`. Invalid indexes or missing names must follow
the underlying JDBC exception behavior; do not silently substitute another
column. Do not swallow errors or fabricate values.

## Detailed Implementation Nodes of Functions

### Node 1: Ordered Array Conversion

Read `ResultSetMetaData.getColumnCount()` and call `getObject(1)` through
`getObject(count)` in order for the current row.

### Node 2: Case-Insensitive Map Conversion

Resolve each column key from label, name, or one-based index, preserve original
key spelling and insertion order, and make lookups case-insensitive.

### Node 3: First-Row Array and Map Handlers

Advance exactly as required by the handler contract, process only the first
row, and return the documented empty array or `null` for no rows.

### Node 4: Scalar Selection

Select the configured one-based index or column name from the first row. Keep
generic return behavior and preserve SQL NULL.

### Node 5: Column List Selection

Iterate all rows, select the configured index or name, and append values in
source order without filtering nulls.

### Node 6: JDBC Exception Behavior

Let `SQLException` cross the public method boundary unchanged. Do not replace
it with a generic runtime exception or use a database-specific workaround.

### Node 7: Maven Project Layout

Use the exact packages and signatures above, compile with Java 21, and keep
the runtime closure empty. Candidate Maven metadata must not control tests.

### Node 8: Offline and Deterministic Execution

Do not access a network, filesystem database, environment service, H2,
Mockito, or Maven Central. The verifier uses only a JDK dynamic-proxy fixture
for `ResultSet` and `ResultSetMetaData`.
