# Introduction and Goals of the Joda-Convert Project

Joda-Convert provides a small annotation-based contract for converting Java objects to and from text. This task isolates the two public annotations used to mark conversion methods and constructors. Implement the exact annotation declarations with the Java standard library only.

## Natural Language Instruction (Prompt)

Create a Java Maven project that provides `org.joda.convert.FromString` and `org.joda.convert.ToString`. Put source under `src/main/java/org/joda/convert` and preserve the exact package names, annotation names, targets, and runtime retention behavior described below. Do not implement the conversion manager or reflection-based converter discovery.

## Environment Configuration

### Core Dependency Library Versions

```text
Temurin JDK 21.0.12+8
Maven 3.9.11
Linux amd64, glibc
Runtime dependencies: none
Network access: unavailable during agent, candidate, verifier, Oracle, and control execution
```

The candidate `pom.xml` is metadata only. It must not add dependencies, plugins, profiles, repositories, modules, extensions, or custom test commands. The verifier compiles candidate code separately and owns grading, collection, JUnit, and reward reports.

## Joda-Convert Project Architecture

### Project Directory Structure

```text
workspace/
├── pom.xml
└── src/main/java/org/joda/convert/
    ├── FromString.java
    └── ToString.java
```

## API Usage Guide

### Core APIs

Implement these exact public annotation types:

```java
package org.joda.convert;

@java.lang.annotation.Target({java.lang.annotation.ElementType.METHOD, java.lang.annotation.ElementType.CONSTRUCTOR})
@java.lang.annotation.Retention(java.lang.annotation.RetentionPolicy.RUNTIME)
public @interface FromString { }

@java.lang.annotation.Target(java.lang.annotation.ElementType.METHOD)
@java.lang.annotation.Retention(java.lang.annotation.RetentionPolicy.RUNTIME)
public @interface ToString { }
```

`FromString` marks one static method or one constructor that can create an object from a `String`. Its public annotation metadata must allow only `METHOD` and `CONSTRUCTOR`, and it must remain available through runtime reflection. `ToString` marks one instance method that returns the textual form. Its metadata must allow only `METHOD`, and it must also remain available through runtime reflection.

### Actual Usage Modes

Apply `@FromString` to a static factory method receiving a `String` or to a constructor receiving a `String`. Apply `@ToString` to an instance method with no parameters that returns `String`. The annotations only declare metadata; they do not invoke methods, validate signatures, perform conversion, or mutate objects.

### Supported Function Types

The supported function types are annotation declaration, runtime retention, target-set metadata, and reflective presence on permitted declaration elements. Annotation order in source does not change behavior. No other annotations, repeatable container, class target, field target, parameter target, or package target is required.

### Error Handling

Java's annotation compiler rules enforce the declared targets. Applying `FromString` or `ToString` to a declaration outside its target set must be rejected by the compiler. The annotations themselves have no methods, arguments, defaults, I/O, external state, or runtime conversion errors.

## Detailed Implementation Nodes of Functions

### Node 1: FromString declaration metadata

Declare `org.joda.convert.FromString` as a public annotation with runtime retention and exactly the method and constructor target set. It must have no annotation elements.

### Node 2: ToString declaration metadata

Declare `org.joda.convert.ToString` as a public annotation with runtime retention and exactly the method target. It must have no annotation elements.

### Node 3: Permitted reflective use

Runtime reflection must observe each annotation on an appropriately annotated method or constructor. A method annotation must not appear on an unannotated member, and the two annotation types must remain distinct.

### Node 4: Declaration boundaries

The target sets are part of the API. `FromString` permits constructors and methods; `ToString` permits methods only. Do not broaden either set or add `@Inherited`, `@Repeatable`, `@Documented`, or unrelated metadata.
