# Introduction and Goals of the ClassGraph Project

## Natural Language Instruction (Prompt)

Implement the bounded `GraphVizDotFileOptions` configuration API from ClassGraph. Your
submission is a Maven project whose Java sources are under `src/main/java`. The public
type must be `io.github.classgraph.viz.GraphVizDotFileOptions`. Reproduce the documented
default values, option transitions, and fluent return behavior described below. Do not
implement classpath scanning, GraphViz rendering, file access, reflection scans, or network
access; those are outside this task.

## Environment Configuration

### Core Dependency Library Versions

Use Temurin JDK `21.0.12+8`, Maven `3.9.11`, and Linux `amd64` with glibc. Candidate
execution, verification, and Oracle execution have no network access. The candidate
`pom.xml` is metadata-only: it may identify the project but must not add dependencies,
plugins, profiles, repositories, modules, parent configuration, reporting, or build
configuration. This bounded slice has an empty Maven dependency closure.

## ClassGraph Project Architecture

This task isolates the options object used by ClassGraph's GraphViz generators. It is a
mutable configuration value that starts with documented defaults and is changed through
fluent methods. The object does not perform scanning or rendering by itself.

### Project Directory Structure

Place the implementation at:

```text
src/main/java/io/github/classgraph/viz/GraphVizDotFileOptions.java
pom.xml
```

The package and public class name are part of the API contract.

## API Usage Guide

### Core APIs

Import `io.github.classgraph.viz.GraphVizDotFileOptions`.

`public GraphVizDotFileOptions()` creates an options object. Its defaults are layout size
`10.5f` by `8.0f`; fields, field-type dependency edges, methods, method-type dependency
edges, annotations, annotation dependency edges, and simple names are enabled. The
external-class choice is unset and therefore represented as `null` until explicitly set.

`public GraphVizDotFileOptions setLayoutSize(float sizeX, float sizeY)` stores both layout
dimensions exactly, including ordinary finite values, and returns the same object. This
method does not clamp or reject values.

The paired zero-argument methods `showFields()` and `hideFields()` set the field display
choice to `true` and `false`; `showFieldTypeDependencyEdges()` and
`hideFieldTypeDependencyEdges()` set field-type edges; `showMethods()` and `hideMethods()`
set method display; `showMethodTypeDependencyEdges()` and
`hideMethodTypeDependencyEdges()` set method-type edges; `showAnnotations()` and
`hideAnnotations()` set annotation display; `showAnnotationDependencyEdges()` and
`hideAnnotationDependencyEdges()` set annotation edges. Each method returns the same
object and repeated calls are deterministic.

`useSimpleNames()` sets simple-name rendering to `true`, while
`useFullyQualifiedNames()` sets it to `false`. `includeExternalClasses()` sets the
external-class choice to `true`, while `excludeExternalClasses()` sets it to `false`.
Each returns the same object. Calling methods in sequence leaves the value from the last
method in each pair, and changing one option does not reset the others.

### Actual Usage Modes

Construct an object and chain options, for example:

```java
GraphVizDotFileOptions options = new GraphVizDotFileOptions()
    .setLayoutSize(12.0f, 8.0f)
    .hideFields()
    .hideMethods()
    .useFullyQualifiedNames()
    .excludeExternalClasses();
```

The return value of every mutator is the original object, so either chained calls or
separate calls on one object are valid.

### Supported Function Types

The supported functions are the public constructor, the layout setter, and the sixteen
zero-argument show/hide or naming/external-class toggles listed above. Inputs are Java
`float` values for layout and no arguments for toggles. State is local to one object and
there are no external side effects.

### Error Handling

No method in this bounded contract throws for ordinary float values, including negative,
zero, or non-finite values. The toggle methods have no exceptional input path. Do not
introduce validation that is not described here.

## Detailed Implementation Nodes of Functions

1. Preserve the exact package, public final class name, public signatures, and default
   values above.
2. Store both arguments of `setLayoutSize` independently and return `this`.
3. Implement each paired toggle as a direct assignment of its corresponding boolean, and
   preserve unrelated option state.
4. Keep the external-class choice tri-state: default unset, then true or false after the
   corresponding public method.
5. Keep the implementation deterministic, in-memory, and free of network, filesystem,
   clock, thread, reflection, and scanning behavior.
