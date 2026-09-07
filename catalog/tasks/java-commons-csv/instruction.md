## Project Description

Create a small, offline Maven project that recreates the verified public slice
of Apache Commons CSV in package `org.apache.commons.csv`. The project is a
library, not a command-line application. A caller supplies CSV text and a
format, obtains records in source order, reads fields, and can format values
using the default format.

The implementation must be independently written. Do not copy an upstream
implementation, upstream tests, private verifier code, or an algorithm body.
Implement the observable contract below with ordinary Java 21 source files.

### Natural Language Instruction

Build a single-module Maven project named Commons CSV with these capabilities:

1. Expose `org.apache.commons.csv.CSVFormat` and its public default format.
2. Parse a supplied `String` with `CSVParser.parse(String, CSVFormat)`.
3. Expose ordered `CSVRecord` objects from the parser.
4. Read record fields by the documented positional or header-name lookup.
5. Report the number of fields with `CSVRecord.size()`.
6. Format a record with `CSVFormat.format(Object...)` using deterministic CSV
   quoting, delimiters, and line separators.
7. Preserve quoted delimiters, escaped quotes, empty fields, and record order.
8. Keep the implementation usable from an empty workspace with offline Maven.

The public import package is exactly `org.apache.commons.csv`. The verifier
loads classes through a child-side Java adapter; do not add a special verifier
entry point or a hidden shortcut. No network, filesystem outside the supplied
Maven workspace, clock, random source, locale-sensitive behavior, or external
service may affect results.

## Supports

### Runtime and Build

- Language: Java.
- Runtime: Temurin JDK `21.0.12+8`.
- Platform: Debian Bookworm, Linux amd64, glibc.
- Package manager: Maven `3.9.11`.
- Build commands are ordinary Maven commands, including `mvn --offline
  validate`; the project must compile with Java release 21.
- Runtime dependencies: none are declared by this task. Use Java standard
  library types such as `String`, `List`, `Iterator`, and `IOException` where
  the public contract requires them.
- The agent, candidate, verifier, Oracle, and controls run with no network.
  They must not access GitHub, codeload, Maven Central, DNS, or any external
  service during execution.

### Project Directory Structure

Use `workspace/` as the project root and create the package path that appears
in every import below:

```text
workspace/
|-- pom.xml
`-- src/
    `-- main/
        `-- java/
            `-- org/
                `-- apache/
                    `-- commons/
                        `-- csv/
                            |-- CSVFormat.java
                            |-- CSVParser.java
                            `-- CSVRecord.java
```

`pom.xml` is the Maven installation/build entry point. Keep the public classes
under `src/main/java/org/apache/commons/csv/`. Package-private helper classes
are allowed only when they do not change the public package contract.

### Scope Boundary

The scoped inventory binds the three classes and four symbols documented below.
Streaming parser builder variants, database `ResultSet` integration, release
configuration, Maven plugins, publishing configuration, and unrelated
upstream APIs are excluded. Those features are **not confidently bindable**
from this task's public inventory and must not be invented as requirements.

### Input and Output Model

CSV input is Java text supplied as a `String`. A format determines delimiters,
quoting, and line handling. Parsed records retain field order and decoded
contents. Formatting returns a Java `String`; it must not write files or print
to standard output. Null and malformed inputs follow the public Java exception
contract and must not be silently repaired.

## API Usage Guide

### `org.apache.commons.csv.CSVFormat`

Import path:

```java
import org.apache.commons.csv.CSVFormat;
```

`CSVFormat` is the immutable description of CSV syntax used by parsing and
formatting. A format controls at least the default comma delimiter, quote
handling, record separator, and header mapping behavior exposed by the task.
Do not make a shared format mutable: creating or using a parser must not alter
the format observed by a later caller.

#### `CSVFormat.DEFAULT`

Signature: `public static final CSVFormat DEFAULT`.

`DEFAULT` is the deterministic default format. It uses comma-separated fields
and the standard quoting rules required by the task. The value is reusable
between calls and has no per-call cursor or record state.

Input domain: no argument is supplied; callers may pass this constant to the
parser or use it to format values. It is not a replacement for a null format.

Return shape and side effects: the value is a `CSVFormat`; reading it has no
side effect and does not access the network or filesystem.

Exceptions: accessing the constant does not throw. Operations receiving a null
format must reject that invalid input with the implementation's unchecked null
argument exception rather than selecting a hidden default.

Normal example:

```java
CSVParser parser = CSVParser.parse("name,age\nAda,37\n", CSVFormat.DEFAULT);
```

Edge example: formatting a value containing a comma with `DEFAULT` quotes the
field so a later parse does not turn one value into two fields.

#### `CSVFormat#format(Object...)`

Import path: `org.apache.commons.csv.CSVFormat`.

Signature: `public String format(Object... values)`.

Input domain: zero or more record values in varargs order. Values may be Java
objects accepted by the library's normal string conversion; an empty varargs
array represents an empty record. The method must escape or quote a value that
contains the delimiter, quote character, or record separator.

Return type and shape: returns one deterministic `String` containing the
formatted fields in the exact input order and the format's record separator.
It does not return a list, mutate the values, or reorder fields.

Side effects: no global state, file, network, clock, or random access. The
format object remains reusable after the call.

Exceptions: invalid null arguments or an unsupported value must use the public
unchecked argument contract; this method does not hide an invalid input by
changing it to a different field. The method does not perform checked I/O.

Normal example:

```java
String line = CSVFormat.DEFAULT.format("Ada", 37);
CSVParser parser = CSVParser.parse(line, CSVFormat.DEFAULT);
```

Edge example:

```java
String line = CSVFormat.DEFAULT.format("a,b", "say \"hi\"");
```

The returned line must quote the comma and escape the embedded quote so parsing
it produces exactly two original field values.

### `org.apache.commons.csv.CSVParser`

Import path:

```java
import org.apache.commons.csv.CSVParser;
```

`CSVParser` represents records parsed from one input. Its record sequence is
ordered, and each record is an `org.apache.commons.csv.CSVRecord`. The parser
must not expose candidate-controlled verifier files or require a CLI.

#### `CSVParser#parse(String, CSVFormat)`

Signature: `public static CSVParser parse(String input, CSVFormat format) throws IOException`.

Input domain: `input` is the complete CSV text to parse; `format` is a
non-null `CSVFormat`. Preserve all logical records in source order, including
empty fields. Delimiters and newlines inside a quoted field are data, not
record boundaries. A final record separator must not create an invented extra
record.

Return type and shape: returns a `CSVParser` containing the parsed sequence.
The parser is iterable according to the class's public Java contract; iteration
must expose `CSVRecord` values in source order. Do not return null for valid
input, and do not return a partially successful parser after malformed input.

Side effects: parsing consumes only the supplied string. It must not access
files, environment variables, network services, locale state, or wall-clock
time. Repeated calls with equal input and format produce equivalent records.

Exceptions: null input or format is invalid and must raise the implementation's
unchecked null-argument exception. Malformed quoting or an invalid CSV state
must raise the library's public unchecked parse exception, if one is exposed;
an input/output adaptation failure is reported as `IOException` by this
signature. Never silently drop malformed trailing data.

Normal example:

```java
try (CSVParser parser = CSVParser.parse("a,b\n1,2\n", CSVFormat.DEFAULT)) {
    for (CSVRecord record : parser) {
        System.out.println(record.get(0));
    }
}
```

Edge example:

```java
CSVParser parser = CSVParser.parse("\"a,b\",\"line\nbreak\"\n",
        CSVFormat.DEFAULT);
CSVRecord record = parser.iterator().next();
```

The record has two fields, `a,b` and `line\nbreak`, despite both delimiter and
newline characters appearing inside quoted fields.

### `org.apache.commons.csv.CSVRecord`

Import path:

```java
import org.apache.commons.csv.CSVRecord;
```

`CSVRecord` is one immutable ordered row returned by `CSVParser`. Its fields
are decoded text values. Empty fields count toward its size and remain in their
original positions.

#### `CSVRecord#get(int)`

Signature: `public String get(int index)`.

Input domain: `index` is zero-based and must satisfy `0 <= index < size()`.
Negative and out-of-range indexes are invalid.

Return type and shape: returns the decoded `String` at that position. It does
not include syntactic quote characters or escape doubling. The operation is
deterministic and does not alter the record or parser cursor.

Side effects: none. Calling `get` repeatedly with the same index returns the
same field value and cannot reorder or remove fields.

Exceptions: invalid indexes raise the public unchecked bounds exception, such
as `IndexOutOfBoundsException`. A record does not return null merely because a
field is empty; an empty CSV field is the empty string.

Normal example:

```java
CSVRecord record = CSVParser.parse("Ada,37\n", CSVFormat.DEFAULT)
        .iterator().next();
String name = record.get(0); // "Ada"
```

Edge example: for `a,,c`, `record.get(1)` returns `""`, while `record.get(3)`
raises the bounds exception.

#### `CSVRecord#get(String)`

Signature: `public String get(String name)`.

Input domain: `name` is a non-null header name available in the record's
configured header mapping. Matching is deterministic and follows the format's
case-sensitivity and duplicate-header policy; do not normalize names by locale.

Return type and shape: returns the decoded field `String` associated with the
header name. Header lookup does not add names or change positional order.

Side effects: none. An unknown lookup must not mutate the header map or create a
new field.

Exceptions: null or unknown names raise the public unchecked lookup/argument
exception rather than returning a value from another column. Header names are
not accepted when no header mapping is configured.

Normal example:

```java
// Use the task's public header configuration on CSVFormat when available.
CSVRecord record = parser.iterator().next();
String age = record.get("age");
```

Edge example: `record.get("missing")` fails deterministically and never
silently returns the first field.

#### `CSVRecord#size()`

Signature: `public int size()`.

Input domain: no arguments.

Return type and shape: returns the non-negative number of fields in this row,
including empty fields. The value is stable for the lifetime of the record.

Side effects and ordering: none; calling it repeatedly does not consume an
iterator or change parser state.

Exceptions: a valid record size query does not throw. It must not return null,
and it must not report a negative value for an empty record.

Normal example:

```java
CSVRecord record = CSVParser.parse("a,b\n", CSVFormat.DEFAULT)
        .iterator().next();
int columns = record.size(); // 2
```

Edge example: `a,,c` has size `3`; the empty middle field is counted.

### Not Confidently Bindable

The scoped inventory does not bind a streaming parser builder, database
integration, command-line entry point, Maven publishing API, or a separate
printer class. These are intentionally omitted rather than guessed. Do not
add public requirements for APIs that are absent from the source-backed
inventory.

## Implementation Notes

- Keep all public classes in `org.apache.commons.csv`; imports, Maven source
  layout, and class names must agree exactly.
- Keep parser, record, and format state instance-local and deterministic. Do
  not use static mutable buffers, random values, current time, system locale,
  environment variables, or unordered maps for observable output.
- Preserve source order at every boundary: input records, fields inside a
  record, varargs values passed to `format`, and header-name resolution.
- Quoted delimiters and newlines are field data. Doubled quote characters in a
  quoted field decode to one quote in the returned `String`.
- Empty input must not produce a fabricated field or record. Empty fields
  between delimiters must remain addressable and count in `size()`.
- A trailing line separator must not add an extra data record. A quoted newline
  must remain part of its field.
- Preserve checked `IOException` behavior on the parse signature. Do not catch
  an error and report a successful partial parser.
- Use `String` conversion for formatting consistently. Do not use locale-
  dependent number/date formatting or implementation-dependent collection
  iteration.
- Small verifiable examples:

  ```text
  parse "name,age\nAda,37\n" -> ["name", "age"], ["Ada", "37"]
  ```

  ```text
  parse "a,,c\n" -> one record of size 3, with field 1 equal to ""
  ```

  ```text
  format ["a,b", "c"] -> a quoted first field, then c, in that order
  ```

  ```text
  parse "\"a\"\"b\",c\n" -> first field "a\"b", second field "c"
  ```

- These examples specify observable behavior, not an algorithm. Choose any
  implementation that meets them and the public signatures.
- The verifier runs offline and separately from the candidate. Do not write
  trusted reports, grader data, hidden tests, or private artifact references
  from candidate code.
- Do not add a network client, shell escape, native dependency, or generated
  source fetched at build time. Maven validation and Java compilation must be
  reproducible from the workspace and the locked offline environment.
