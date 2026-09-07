## Project Description

Recreate a small, deterministic Java library slice from Gson for applications that need to
translate Java reflection field names into JSON field names. The project is intended for users
who configure a naming convention at an integration boundary and for callers who inspect the
metadata on serialized fields. The deliverable is a compilable Maven project, not a complete
JSON serializer.

The in-scope public surface is limited to the following packages and types:

- `com.google.gson.FieldNamingStrategy`, an interface for translating a reflected field name and
  for supplying alternative deserialization names.
- `com.google.gson.FieldNamingPolicy`, the standard enum strategies supplied by this bounded
  slice.
- `com.google.gson.annotations.SerializedName`, a runtime annotation containing a primary name
  and optional alternative names.

The candidate must preserve the exact package names, type names, public method signatures, enum
constant names, annotation members, and Java visibility required below. Calls must work with
`java.lang.reflect.Field` values obtained from ordinary user classes. The implementation must be
stateless: translating one field must not modify the field, the declaring class, a policy object,
or process-wide state.

The naming policies operate on `Field.getName()`. They do not serialize values, parse JSON, create
`Gson` instances, scan a class, discover adapters, access files, contact a network, or run a
command-line interface. `Gson`, `GsonBuilder`, JSON tree types, reflection access management,
and unrelated Gson annotations are outside this task. Do not add a substitute serializer or a
dependency on the full Gson distribution.

The implementation should be useful for both ordinary camel-case names and deliberately awkward
names containing leading underscores, existing separators, digits, acronyms, or non-ASCII
letters. Preserve characters that the selected policy does not explicitly transform. Results
must be repeatable on every supported machine and must not depend on the default process locale.

### Natural Language Instruction

Build the Maven project described by this specification from an empty `workspace/` directory.
Provide the three public Java types at their exact package paths, compile them for Java 21, and
keep the project usable without network access. Implement all seven naming policy constants, both
methods of the strategy interface, and both annotation members with the signatures and metadata
below. Preserve the distinction between field-name translation and annotation metadata: this
bounded project supplies the public contracts but does not implement a JSON engine. Do not add
unverified public APIs, alternate package names, a command-line wrapper, or dependencies that
would require Maven to contact a repository.

## Supports

### Runtime and Build

- Operating system: Debian Bookworm on `linux/amd64` with glibc.
- Java runtime: Temurin JDK `21.0.12+8`.
- Java release level: compile with `--release 21`.
- Package manager and build tool: Apache Maven `3.9.11`.
- The harness runs Maven and Java compilation offline. Do not expect a package index, Git host,
  DNS service, or external HTTP service at build or test time.
- The bounded implementation uses only JDK classes, especially `java.lang.reflect.Field`,
  `java.lang.annotation`, `java.util.Locale`, `java.util.Collections`, and `java.util.List`.
- There are no runtime packages to download. Do not introduce third-party dependencies, vendored
  jars, repository declarations, plugins, profiles, parent POMs, modules, or network setup in the
  candidate POM.

### Offline Setup Contract

Create a metadata-only `pom.xml` at the workspace root. It may identify the project and its
coordinates, but the candidate project must remain compilable with the JDK-only source surface
described here. The harness performs the setup and verification commands; the candidate does not
need to provide an installer, executable, shell script, server, or CLI.

The public build entry point is the Maven project root. The source compilation entry point is the
Java source tree under `src/main/java`. The verifier may compile a small caller with `javac
--release 21` against the candidate classes, so public classes and annotation metadata must be
available from their declared package paths. There is no supported command such as `gson` or
`java -jar` for this task.

### Project Directory Structure

Use this layout from an empty workspace. `workspace/` is the project root, not a package name.

```text
workspace/
├── pom.xml
└── src/
    └── main/
        └── java/
            └── com/
                └── google/
                    └── gson/
                        ├── FieldNamingPolicy.java
                        ├── FieldNamingStrategy.java
                        └── annotations/
                            └── SerializedName.java
```

Do not move the classes into a default package or a similarly named replacement package. The
directory tree and Java `package` declarations must agree. No CLI entry point, resource file,
database, generated file, test fixture, or external service configuration is required.

## API Usage Guide

### `com.google.gson.FieldNamingStrategy`

Declare the public interface at `src/main/java/com/google/gson/FieldNamingStrategy.java`.

Callers import the type normally:

```java
import com.google.gson.FieldNamingPolicy;
import com.google.gson.FieldNamingStrategy;
import com.google.gson.annotations.SerializedName;
```

```java
public interface FieldNamingStrategy {
  String translateName(java.lang.reflect.Field f);
  default java.util.List<String> alternateNames(java.lang.reflect.Field f);
}
```

`translateName(Field f)` accepts one reflected field and returns one `String`, the JSON-facing
  name selected for that field. The method must use the supplied field's name as its input for
  the standard policies. It has no file, network, time, random, or global-state side effect.
  The returned string is deterministic for the same field and strategy. A caller should pass a
  non-null `Field`; null is outside the useful input domain and implementations must not invent a
  separate string-input overload.

Example:

```java
final class Record {
  int accountId;
}
java.lang.reflect.Field field = Record.class.getDeclaredField("accountId");
String name = com.google.gson.FieldNamingPolicy.LOWER_CASE_WITH_DASHES
    .translateName(field);
// name is "account-id"
```

An empty-name string cannot be obtained from a valid Java field declaration. A field such as
`int value` has no special state and can be translated repeatedly with the same result. The
interface itself does not prescribe a checked exception; reflection lookup can throw the normal
`NoSuchFieldException` before the API call, while a null field is invalid input and should not be
used as a portable contract.

`alternateNames(Field f)` is a Java 8-compatible default method with return type
`java.util.List<String>`. The default implementation returns an empty list because a strategy
has no alternative names unless it explicitly supplies them. The empty result is ordered and
deterministic; callers must treat it as read-only. It does not mutate the field or strategy.

Example:

```java
java.util.List<String> aliases =
    com.google.gson.FieldNamingPolicy.IDENTITY.alternateNames(field);
// aliases is empty
```

The default method is not a second naming transformation and does not derive aliases from the
field name. The bounded policy enum uses this default behavior.

### `com.google.gson.FieldNamingPolicy`

Declare the public enum at `src/main/java/com/google/gson/FieldNamingPolicy.java` and make it
implement `FieldNamingStrategy`. It must expose exactly these constants in this order:

```java
IDENTITY,
UPPER_CAMEL_CASE,
UPPER_CAMEL_CASE_WITH_SPACES,
UPPER_CASE_WITH_UNDERSCORES,
LOWER_CASE_WITH_UNDERSCORES,
LOWER_CASE_WITH_DASHES,
LOWER_CASE_WITH_DOTS
```

Each constant implements the inherited callable
`public String translateName(java.lang.reflect.Field f)`. The input is a non-null reflected
field; the source text is `f.getName()`. The result is a new or reused immutable Java string and
does not alter the `Field`. The enum constants are singleton values and contain no mutable
per-call state. `alternateNames(Field)` remains the interface default and returns an empty list.

#### `IDENTITY.translateName(Field)`

Return `f.getName()` unchanged. Do not insert separators, change case, normalize underscores, or
apply locale rules. For a field named `accountId`, the result is `accountId`. For `_9` or
`already_lower`, the punctuation and digits remain exactly as declared. A missing reflected field
is a reflection lookup error before translation; do not accept a raw string in place of `Field`.

#### `UPPER_CAMEL_CASE.translateName(Field)`

Find the first character in the field name for which Java `Character.isLetter` is true. If that
character is lowercase, replace it with `Character.toUpperCase` while preserving every earlier
and later character. If it is already uppercase, return the name unchanged. If no character is a
letter, return the name unchanged. This is character-based behavior, not word splitting and not
default-locale conversion.

For `someField`, return `SomeField`; for `_someField`, return `_SomeField`; for `_9`, return
`_9`. A leading underscore or digit is preserved before the first letter. An existing uppercase
letter is not lowercased or otherwise normalized.

#### `UPPER_CAMEL_CASE_WITH_SPACES.translateName(Field)`

First insert a space before each uppercase character after the first output character, then apply
the same first-letter capitalization rule as `UPPER_CAMEL_CASE`. The separator test uses Java
`Character.isUpperCase`; existing separators are preserved and can therefore be adjacent to an
inserted space. This policy does not collapse runs of uppercase letters.

For `someFieldName`, return `Some Field Name`. For `_someField`, return `_Some Field`; for
`aURL`, the uppercase run is separated character by character and produces `A U R L`. A name with
no uppercase characters receives no inserted spaces, apart from capitalization of its first
letter when applicable.

#### `UPPER_CASE_WITH_UNDERSCORES.translateName(Field)`

Insert `_` before each uppercase character after the first output character, then convert the
complete result with `String.toUpperCase(Locale.ENGLISH)`. Existing underscores are not removed;
an existing underscore followed by an uppercase character can consequently produce two
underscores. The use of `Locale.ENGLISH` makes the result independent of the process default
locale.

For `someFieldName`, return `SOME_FIELD_NAME`; for `_someField`, return `_SOME_FIELD`; for
`aURL`, return `A_U_R_L`. For `_UpperCamel`, the leading underscore is preserved and the uppercase
`U` is separated according to the same character rule.

#### `LOWER_CASE_WITH_UNDERSCORES.translateName(Field)`

Insert `_` before each uppercase character after the first output character, then convert the
complete result with `String.toLowerCase(Locale.ENGLISH)`. Do not remove existing underscores or
change separators other than case conversion. For `someFieldName`, return `some_field_name`; for
`UpperCamel`, return `upper_camel`; for `aURL`, return `a_u_r_l`.

#### `LOWER_CASE_WITH_DASHES.translateName(Field)`

Insert `-` before each uppercase character after the first output character, then apply
`String.toLowerCase(Locale.ENGLISH)`. A dash is part of the returned JSON field-name string; it is
not a Java identifier and must not be changed to an underscore. For `someFieldName`, return
`some-field-name`; for `_someField`, return `_some-field`; for `aURL`, return `a-u-r-l`.

#### `LOWER_CASE_WITH_DOTS.translateName(Field)`

Insert `.` before each uppercase character after the first output character, then apply
`String.toLowerCase(Locale.ENGLISH)`. The dot remains data in the returned field name and does
not mean that a nested Java property should be traversed. For `someFieldName`, return
`some.field.name`; for `_someField`, return `_some.field`; for `aURL`, return `a.u.r.l`.

#### Policy edge behavior

All separator policies preserve characters before the first output character and all characters
that are not uppercase according to `Character.isUpperCase`. Names such as `__`, `_123`, and
`lower_words` remain deterministic. A non-ASCII letter is considered using Java's character
classification and case conversion methods; do not substitute ASCII-only regular expressions.
The three lower/upper separator policies must continue to use `Locale.ENGLISH`, even when the
caller changes `Locale.getDefault()` to a locale with special casing rules.

### `com.google.gson.annotations.SerializedName`

Declare the public annotation at
`src/main/java/com/google/gson/annotations/SerializedName.java`.

```java
@java.lang.annotation.Documented
@java.lang.annotation.Retention(java.lang.annotation.RetentionPolicy.RUNTIME)
@java.lang.annotation.Target({
    java.lang.annotation.ElementType.FIELD,
    java.lang.annotation.ElementType.METHOD
})
public @interface SerializedName {
  String value();
  String[] alternate() default {};
}
```

`value()` is required and returns one `String`, the primary serialized/deserialized name. The
annotation declaration must reject an omitted `value` at Java source compile time in the normal
annotation manner. An ordinary use is `@SerializedName("account_id")` on a field. The value is
metadata; this bounded task does not require implementing a serializer that consumes it.

`alternate()` returns a `String[]` and defaults to a newly presented empty annotation value when
the member is omitted. It is intended to describe alternative deserialization names. An ordinary
declaration is `@SerializedName(value = "account_id", alternate = {"accountId", "acct"})`.
The order supplied by the annotation source is observable through reflection and must be
preserved. An empty `alternate` array is valid. Do not silently invent trimming, case folding,
deduplication, validation, or serialization behavior for these strings.

The annotation must be visible through runtime reflection and applicable to fields and methods.
It must not be limited to source-only retention or made applicable to unrelated declaration kinds.
The annotation itself has no I/O or global-state side effect. This task does not require the
annotation to override a policy at runtime because no `Gson` serializer is part of the contract.

## Implementation Notes

Keep the implementation within the three declared public types and the JDK. Match Java package
and file paths exactly; Maven metadata must not cause an online dependency resolution. The
candidate should compile under `javac --release 21` and under the harness's offline Maven setup.

The naming implementation should read the field name once per operation and use deterministic
character traversal. Do not use the default locale, current time, random values, reflection over
unrelated classes, thread-local hidden configuration, or mutable static caches. A policy call
must be safe to repeat with the same `Field` and must return the same value after calls on other
fields.

The separator rule is intentionally character-oriented. For every character in the source name,
an uppercase character causes a separator only when the translated prefix already has a
character. This means existing punctuation is data, repeated uppercase characters are each
handled, and acronym words are not grouped heuristically. The first-letter rule is separate: it
searches for the first Java letter and changes at most that letter.

Use `Locale.ENGLISH` explicitly for `UPPER_CASE_WITH_UNDERSCORES`,
`LOWER_CASE_WITH_UNDERSCORES`, `LOWER_CASE_WITH_DASHES`, and `LOWER_CASE_WITH_DOTS`. The camel
case policies use `Character` case methods and do not need a locale. Keep `FieldNamingPolicy`
stateless and let `FieldNamingStrategy.alternateNames` retain its empty-list default.

Small verifiable examples:

1. A reflected field named `lowerCamel` maps in enum order to `lowerCamel`, `LowerCamel`,
   `Lower Camel`, `LOWER_CAMEL`, `lower_camel`, `lower-camel`, and `lower.camel`.
2. A reflected field named `_lowerCamel` maps to `_lowerCamel`, `_LowerCamel`, `_Lower Camel`,
   `_LOWER_CAMEL`, `_lower_camel`, `_lower-camel`, and `_lower.camel`.
3. A reflected field named `aURL` maps under the three separator families to `A_U_R_L`,
   `a_u_r_l`, `a-u-r-l`, and `a.u.r.l` as applicable; uppercase characters are not grouped.
4. With the default locale temporarily set to Turkish, the upper/lower separator policies still
   produce the English-locale result for a field named `iValue` or `IValue`.
5. Runtime reflection on `@SerializedName(value = "id", alternate = {"identifier"})` returns
   `id` from `value()` and the one-element ordered array from `alternate()`.

Do not implement the full Gson library, JSON parsing, field discovery, adapter registration,
serialization, deserialization, command-line behavior, or network access. Do not copy source
function bodies or private tests into the project. The required result is the observable public
contract above, with ordinary Java exceptions and compile-time annotation rules preserved.
