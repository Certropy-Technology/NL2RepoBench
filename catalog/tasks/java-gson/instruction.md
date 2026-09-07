# Introduction and Goals of the Gson Project

## Natural Language Instruction (Prompt)

Recreate the bounded public field-naming policy slice of the Gson project. Implement the public
types and behavior described below under the exact Java packages and signatures. The implementation
must compile on Java 21 with a metadata-only Maven POM and must not download dependencies or use
the network. Do not implement Gson serialization, reflection scanning, adapters, or unrelated APIs.

## Environment Configuration

### Core Dependency Library Versions

Use Temurin JDK `21.0.12+8`, Maven `3.9.11`, Linux `amd64` with glibc. Runtime and verification
are offline. The candidate `pom.xml` is metadata-only: it may identify the project but must not
declare dependencies, plugins, profiles, repositories, modules, a parent POM, or other build
configuration. The contract uses only JDK `java.lang.reflect.Field`, `java.lang.annotation`, and
`java.util.Locale`.

## Gson Project Architecture

### Project Directory Structure

Place Java sources under `src/main/java`. The required packages are
`com.google.gson` and `com.google.gson.annotations`. A normal metadata-only `pom.xml` belongs at
the project root. No external runtime library is needed.

## API Usage Guide

### Core APIs

Implement `com.google.gson.FieldNamingStrategy` with the public method
`String translateName(java.lang.reflect.Field f)`. It returns the JSON field name for the supplied
field and must be deterministic. The argument must be non-null; dereferencing a null field should
follow normal Java null behavior.

Implement `com.google.gson.FieldNamingPolicy`, an enum implementing `FieldNamingStrategy`, with
these constants: `IDENTITY`, `UPPER_CAMEL_CASE`, `UPPER_CAMEL_CASE_WITH_SPACES`,
`UPPER_CASE_WITH_UNDERSCORES`, `LOWER_CASE_WITH_UNDERSCORES`, `LOWER_CASE_WITH_DASHES`, and
`LOWER_CASE_WITH_DOTS`. Each constant supports the inherited public method
`String translateName(Field f)`.

Implement `com.google.gson.annotations.SerializedName` as a runtime field/method annotation with
the public members `String value()` and `String[] alternate()` whose default is an empty array.
The annotation is a dependency of the public strategy interface and is not used to alter
`FieldNamingPolicy` output.

### Actual Usage Modes

Given a class field, obtain a policy constant and call `policy.translateName(MyType.class
 .getDeclaredField("someFieldName"))`. The returned string is the exact transformed name. Policy
objects are stateless and reusable; calls must not mutate the reflected field or global state.

### Supported Function Types

`IDENTITY` returns the field name unchanged. `UPPER_CAMEL_CASE` uppercases the first Unicode
letter, preserving any leading non-letter characters. `UPPER_CAMEL_CASE_WITH_SPACES` additionally
inserts a space before every uppercase character after the first output character. The underscore,
dash, and dot policies insert their respective separator before every uppercase character after
the first character and then apply English-locale upper or lower casing as named.

For example, for a field named `someFieldName`, results are `someFieldName`, `SomeFieldName`,
`Some Field Name`, `SOME_FIELD_NAME`, `some_field_name`, `some-field-name`, and `some.field.name`
in enum order. A leading underscore is preserved, and an acronym such as `aURL` becomes
`A_U_R_L` under the upper-underscore policy.

### Error Handling

The method accepts a `Field` object, not an arbitrary string. A null argument is invalid and may
produce the normal exception from accessing the field name. Fields with no uppercase characters,
leading punctuation, digits, or non-ASCII letters remain deterministic. No policy performs I/O,
network access, time reads, random generation, or background work.

## Detailed Implementation Nodes of Functions

1. Preserve exact package names, enum constants, and the `FieldNamingStrategy` method signature.
2. Derive the source name using `Field.getName()` and preserve all characters other than the
   documented separator and case transformations.
3. Detect uppercase characters with Java character semantics; insert a separator only when the
   output already contains a character, matching camel-case behavior.
4. Apply `Locale.ENGLISH` for the upper/lower underscore, dash, and dot policies so results are
   stable regardless of the process locale.
5. Upper-camel conversion must find the first letter, leave earlier characters intact, and
   uppercase only that letter.
6. Keep the policy stateless and return a new string only when transformation requires it.
7. Define `SerializedName` with runtime retention and field/method targets; `alternate()` defaults
   to an empty array.

