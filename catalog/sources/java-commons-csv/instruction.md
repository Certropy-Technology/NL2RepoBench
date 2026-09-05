# Introduction and Goals of the Commons CSV Project

Apache Commons CSV is a Java library for parsing and formatting delimited
records. This task implements a deterministic public slice covering CSV
format selection, record parsing, field access, iteration, and resource
management. The project must remain a self-contained single-module Maven
library.

## Natural Language Instruction (Prompt)

Please create a Java Maven project named Commons CSV with the following public
behavior:

1. Parse comma-separated text into records while preserving source order.
2. Expose record field access by zero-based index and by header name when a
   header is configured.
3. Support the documented default CSV format and explicit header behavior.
4. Provide deterministic iteration, record counts, and `AutoCloseable`/`close`
   behavior for parsers.
5. Preserve quoted commas, escaped quotes, empty fields, and line boundaries.
6. Keep the implementation under `src/main/java` in a single-module Maven
   project without external runtime dependencies.

## Environment Configuration

### Core Dependency Library Versions

```Plain
Temurin JDK 21.0.12+8       # Java runtime
Maven 3.9.11                # Offline project tooling
Linux amd64                 # Fixed platform
Runtime dependencies: none  # Java standard library only
Network access: unavailable # Agent and verifier are offline
```

## Commons CSV Project Architecture

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
                        └── csv
                            ├── CSVFormat.java
                            ├── CSVParser.java
                            └── CSVRecord.java
```

The candidate POM is metadata only. Do not use candidate-controlled build
plugins, dependencies, profiles, repositories, modules, or custom extensions.

## API Usage Guide

### Core APIs

#### 1. Module Import

```java
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;
```

#### 2. CSVFormat - Select Parsing Rules

```java
CSVFormat format = CSVFormat.DEFAULT;
```

Use the public default format and its documented header configuration methods.
Formatting options must be deterministic and must not depend on locale.

#### 3. CSVParser - Parse Records

```java
try (CSVParser parser = CSVParser.parse("a,b\n1,2\n", format)) {
    for (CSVRecord record : parser.getRecords()) {
        System.out.println(record.get(0));
    }
}
```

The parser is `AutoCloseable`; `getRecords()` returns records in source order.
The parser must not reorder or silently drop records.

#### 4. CSVRecord - Read Fields

```java
String first = record.get(0);
long number = record.getRecordNumber();
boolean present = record.isMapped("name");
String value = record.get("name");
```

Index access is zero-based. Header-name access follows the configured header
map and reports missing names through the public exception contract.

### Actual Usage Modes

#### Basic Parsing

```java
CSVParser parser = CSVParser.parse("a,b\n1,2\n", CSVFormat.DEFAULT);
List<CSVRecord> records = parser.getRecords();
parser.close();
```

#### Quoted Fields

```java
CSVParser parser = CSVParser.parse("\"a,b\",c\n", CSVFormat.DEFAULT);
CSVRecord record = parser.getRecords().get(0);
// record.get(0) is "a,b"
```

#### Header Access

Configure a header through the public `CSVFormat` API, then use
`record.get("header")` and `record.isMapped("header")` consistently.

### Supported Function Types

The supported function types are format configuration, parser construction,
record collection and iteration, indexed field access, header-name access,
record numbering, and close/resource behavior.

### Error Handling

Malformed quotes, invalid field access, missing header names, null inputs, and
use after close must follow the public exception and lifecycle behavior. Do
not silently repair malformed CSV or change record order.

## Detailed Implementation Nodes of Functions

### Node 1: Default CSV Parsing

Parse comma-separated records using the documented default delimiter and line
handling rules.

### Node 2: Quoting and Escaping

Preserve commas and newlines inside quoted fields and unescape doubled quotes.

### Node 3: Record Ordering

Return records in exact source order and maintain deterministic record numbers.

### Node 4: Indexed Field Access

Implement zero-based access, including empty fields and boundary indexes.

### Node 5: Header Mapping

Implement configured header-name lookup and distinguish mapped names from
missing names without silently returning another field.

### Node 6: Iteration and getRecords()

Make iteration and `getRecords()` consistent, repeatable where promised, and
free from accidental record loss.

### Node 7: AutoCloseable Lifecycle

Implement `close()` and the documented behavior for parser operations after
close while avoiding resource leaks.

### Node 8: Offline Maven Layout

Use the exact public packages, standard Maven source layout, Java 21, and no
network or candidate-controlled Maven build configuration.
