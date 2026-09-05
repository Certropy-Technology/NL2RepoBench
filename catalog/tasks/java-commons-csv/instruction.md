# Project Description

Implement the selected deterministic CSV parsing and formatting behavior of
Apache Commons CSV as a single Maven Java library. The project must parse
ordinary CSV text, expose record fields and sizes, and format values into one
CSV record through the public classes in `org.apache.commons.csv`.

## Introduction and Goals

The library preserves CSV record order, handles quoted commas, exposes
zero-based field access, and formats values using the default comma delimiter.
The evaluator uses a separate offline verifier, an empty private Maven
repository, and a fixed JDK 21/Maven environment.

## Natural Language Instruction (Prompt)

Please create a Java Maven project that provides the following public behavior:

1. `CSVParser.parse(String, CSVFormat)` parses CSV text into records.
2. `CSVRecord.get(int)` returns a field by zero-based index.
3. `CSVRecord.size()` returns the number of fields in a record.
4. `CSVFormat.DEFAULT.format(Object...)` formats values as one CSV record.
5. Preserve ordinary comma-delimited rows, quoted commas, empty fields, record
   order, and deterministic formatting.
6. Keep Java sources under `src/main/java` in a normal single-module Maven
   project without external runtime dependencies.

## Environment Configuration

- Java runtime: Temurin JDK `21.0.12+8`
- Maven: `3.9.11`
- Platform: Linux `amd64`
- Build and verification: offline, verifier-owned Maven/Javac harness
- Candidate compilation: `javac --release 21`
- Runtime dependencies: none
- Network access: unavailable to the agent and verifier

## Project Architecture

Use the standard Maven layout:

```text
project/
├── pom.xml
└── src/
    └── main/
        └── java/
            └── org/apache/commons/csv/
                ├── CSVFormat.java
                ├── CSVParser.java
                └── CSVRecord.java
```

The required public package is `org.apache.commons.csv`. Keep the
implementation self-contained and do not execute the upstream Maven build,
profiles, plugins, tests, or repository configuration.

## API Usage Guide

```java
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;

CSVParser parser = CSVParser.parse("name,value\nAda,42", CSVFormat.DEFAULT);
// The returned parser preserves record order and exposes the parsed records.
parser.close();
String line = CSVFormat.DEFAULT.format("Ada", 42);
```

The required public signatures are:

```java
CSVParser CSVParser.parse(String text, CSVFormat format)
List<CSVRecord> CSVParser.getRecords()
String CSVRecord.get(int index)
int CSVRecord.size()
String CSVFormat.DEFAULT.format(Object... values)
```

`CSVParser` implements `AutoCloseable`; `close()` releases parser resources and
does not change already parsed record values. `getRecords()` returns records in
source order. Quoted fields may contain commas and are unquoted when returned
by `CSVRecord.get(int)`. Formatting uses the default comma delimiter and quotes
values only when CSV syntax requires it.

## Examples and Boundary Conditions

```java
try (CSVParser parser = CSVParser.parse("name,value\nAda,42", CSVFormat.DEFAULT)) {
    parser.getRecords().get(1).get(0); // Ada
    parser.getRecords().get(1).size(); // 2
}
CSVFormat.DEFAULT.format("Ada", 42); // Ada,42
CSVParser.parse("a,\"b,c\"", CSVFormat.DEFAULT); // quoted comma is one field
```

Preserve empty fields, quoted commas, row order, zero-based indexing, and
deterministic output. Malformed input must follow the selected library's
ordinary exception behavior. Do not use network access or external runtime
dependencies.

## Implementation Notes

The verifier compiles candidate sources directly and calls only the selected
public methods through a separate candidate JVM. The candidate `pom.xml` is
validated as metadata; upstream plugins, profiles, repositories, tests,
modules, and release configuration are outside the task contract.
