# Project Description

Implement the selected deterministic CSV parsing and formatting behavior of
Apache Commons CSV as a single Maven Java library. The evaluator uses JDK 21,
an offline empty Maven repository, and a verifier-owned contract harness.

# Supports

Implement the public classes in `org.apache.commons.csv` needed for these
operations:

- `CSVParser.parse(String, CSVFormat)` parses CSV text into records.
- `CSVRecord.get(int)` returns a field by zero-based index.
- `CSVRecord.size()` returns the number of fields in a record.
- `CSVFormat.DEFAULT.format(Object...)` formats values as one CSV record.

The contract covers ordinary comma-delimited rows, quoted commas, field
access, and deterministic formatting. Preserve record order and empty-field
behavior.

# API Usage Guide

```java
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;

try (CSVParser parser = CSVParser.parse("name,value\nAda,42", CSVFormat.DEFAULT)) {
    String first = parser.getRecords().get(1).get(0);
}
String line = CSVFormat.DEFAULT.format("Ada", 42);
```

Parsing returns records in source order. Quoted fields may contain commas and
are unquoted in `CSVRecord.get(int)`. Formatting uses the default comma
delimiter and quotes values only when required by CSV syntax.

# Implementation Notes

Use the standard Maven layout with Java sources under `src/main/java`. The
verifier compiles candidate sources with `--release 21` and uses a fixed
separate JVM contract harness. Do not execute or copy the upstream Maven build,
profiles, plugins, tests, or repository configuration.
