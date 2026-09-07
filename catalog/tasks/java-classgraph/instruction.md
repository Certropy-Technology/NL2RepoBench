## Project Description

Build a small, deterministic Java Maven project that recreates the bounded
`GraphVizDotFileOptions` configuration object from ClassGraph. The project is for an
agent implementing a single in-memory public value/configuration type, not for
recreating the complete ClassGraph distribution. A caller should be able to construct
the object, configure GraphViz-related display choices, and chain the fluent methods.

The bounded public type is:

```java
io.github.classgraph.viz.GraphVizDotFileOptions
```

The object owns configuration state for layout dimensions, field and method display,
dependency-edge display, annotation display, name rendering, and external-class
inclusion. Each option is independent except that the two methods in one show/hide
pair update the same option. The implementation must be deterministic and local to the
object.

This task does not ask for classpath scanning, class loading, GraphViz process
execution, DOT serialization, filesystem access, network access, reflection scans,
logging, concurrency, or a command-line interface. Do not add those features to make
the project appear larger. The public contract is intentionally limited to the one
configuration class and the methods listed in the API Usage Guide.

The implementation should preserve the package name, public type name, public method
signatures, default state, fluent return identity, and independent option transitions.
The Maven project must compile with the stated JDK and with an empty dependency
closure.

## Supports

### Natural Language Instruction

Create a Maven project rooted at `workspace/` and implement
`io.github.classgraph.viz.GraphVizDotFileOptions` under
`src/main/java/io/github/classgraph/viz/GraphVizDotFileOptions.java`.

The implementation must provide these capabilities:

1. Construct an options object with the documented layout and boolean defaults.
2. Store two layout dimensions exactly through `setLayoutSize(float, float)`.
3. Toggle field, field-type-edge, method, method-type-edge, annotation, and
   annotation-edge choices through the corresponding show/hide methods.
4. Toggle simple-name versus fully-qualified-name rendering.
5. Toggle inclusion versus exclusion of external classes while preserving the initial
   unset state until one of those methods is called.
6. Return the same object from every mutator so that calls can be chained.

Do not add public methods or public types as substitutes for the listed contract. In
particular, do not invent getters, builders, constructors with arguments, enums,
serializers, scanners, renderers, or CLI entry points. Hidden evaluation may inspect
the configured state through the task's bounded contract, so use the exact names and
types below.

### Project Directory Structure

The candidate workspace must have this shape:

```text
workspace/
├── pom.xml
└── src/
    └── main/
        └── java/
            └── io/
                └── github/
                    └── classgraph/
                        └── viz/
                            └── GraphVizDotFileOptions.java
```

`GraphVizDotFileOptions.java` must declare the package
`io.github.classgraph.viz`. `pom.xml` is required as Maven project metadata, but it
must remain metadata-only for this task: do not add external dependencies, repositories,
plugins, profiles, modules, parent configuration, or reporting configuration. There is
no public CLI, resource directory, test fixture, or generated file required by this
contract.

### Environment Configuration

Use Temurin JDK `21.0.12+8`, Maven `3.9.11`, Linux `amd64`, and glibc. The candidate
must compile using Java release 21. Candidate, verifier, and Oracle execution are
offline. Do not fetch Maven artifacts, source code, GitHub content, DNS data, or any
other external resource at runtime. The project has an empty Maven dependency closure;
all behavior can be implemented with the Java language and standard platform APIs.

The expected project check is equivalent to:

```text
mvn --offline validate
javac --release 21 <the candidate source and the contract harness>
```

Do not make `pom.xml` depend on the local machine's unrelated Maven settings. A clean
workspace containing only the files in the directory tree above must remain a valid
candidate project.

## API Usage Guide

Every API below is in the package `io.github.classgraph.viz`. Import the type with:

```java
import io.github.classgraph.viz.GraphVizDotFileOptions;
```

The class is a mutable, per-instance configuration object. Its mutators return the
same instance. No method performs I/O, network access, process execution, reflection,
classpath scanning, or global-state mutation. The contract has no public getters; the
configured state is consumed by the surrounding GraphViz code in the original project
and is therefore specified here by its required defaults and transitions.

### `GraphVizDotFileOptions()`

**Signature:**

```java
public GraphVizDotFileOptions()
```

**Inputs and return:** The constructor takes no arguments and returns a new
`GraphVizDotFileOptions` instance. It has no checked or unchecked exception path for
ordinary construction and has no external side effect.

**Initial state:** Set the layout width to `10.5f` and height to `8.0f`. Enable field
display, field-type dependency edges, method display, method-type dependency edges,
annotation display, annotation dependency edges, and simple names. Leave the external
class choice unset until an inclusion or exclusion method is called; that unset state
is distinct from explicitly selecting either value.

**Normal example:**

```java
GraphVizDotFileOptions options = new GraphVizDotFileOptions();
```

**Edge example:** Construct two instances. Changing one later must not change the
other, because configuration state is per instance rather than static or shared.

### `setLayoutSize(float, float)`

**Signature:**

```java
public GraphVizDotFileOptions setLayoutSize(float sizeX, float sizeY)
```

**Inputs:** `sizeX` is the requested layout width and `sizeY` is the requested layout
height. Accept Java `float` values as supplied, including zero, negative, positive
infinity, negative infinity, and `NaN`; this bounded contract does not clamp, round,
or reject them.

**Return and state:** Store both values independently and return the exact receiver
(`this`). The call changes only layout dimensions and does not reset any display,
naming, or external-class option. It has no checked or unchecked exception contract for
the accepted float domain and has no external side effect.

**Normal example:**

```java
GraphVizDotFileOptions options = new GraphVizDotFileOptions()
    .setLayoutSize(12.0f, 8.0f);
```

**Edge example:** `new GraphVizDotFileOptions().setLayoutSize(Float.NaN,
Float.NEGATIVE_INFINITY)` must preserve the two supplied float values rather than
substituting defaults or throwing solely because they are non-finite.

### `showFields()`

**Signature:**

```java
public GraphVizDotFileOptions showFields()
```

This zero-argument method sets the field-display option to `true`, returns the same
receiver, and has no side effect outside that object. It throws no checked or unchecked
exception for its empty input domain. Calling it repeatedly is deterministic.

**Normal example:** `GraphVizDotFileOptions options = new GraphVizDotFileOptions().showFields();`

**Edge example:** After `hideFields().showFields()`, field display is enabled and the
later call does not restore or alter any unrelated option.

### `hideFields()`

**Signature:**

```java
public GraphVizDotFileOptions hideFields()
```

This zero-argument method sets the field-display option to `false`, returns the same
receiver, and has no external side effect. It has no checked or unchecked exception
path for its empty input domain and is deterministic when repeated.

**Normal example:** `GraphVizDotFileOptions options = new GraphVizDotFileOptions().hideFields();`

**Edge example:** Calling `hideFields()` twice must remain equivalent to calling it
once; it must not toggle back to `true`.

### `showFieldTypeDependencyEdges()`

**Signature:**

```java
public GraphVizDotFileOptions showFieldTypeDependencyEdges()
```

Set field-type dependency-edge display to `true`, return the same receiver, and change
no other setting. There are no arguments, checked exceptions, unchecked validation
errors, or external side effects.

**Normal example:** `GraphVizDotFileOptions options = new GraphVizDotFileOptions().showFieldTypeDependencyEdges();`

**Edge example:** `hideFieldTypeDependencyEdges().showFieldTypeDependencyEdges()`
leaves only this edge option restored to enabled; it does not change field visibility.

### `hideFieldTypeDependencyEdges()`

**Signature:**

```java
public GraphVizDotFileOptions hideFieldTypeDependencyEdges()
```

Set field-type dependency-edge display to `false` and return the same receiver. The
method has no arguments, no external side effects, and no checked or unchecked
exception path in this contract.

**Normal example:** `GraphVizDotFileOptions options = new GraphVizDotFileOptions().hideFieldTypeDependencyEdges();`

**Edge example:** Repeating the call must remain disabled rather than acting as a
toggle; calling it must not change method or annotation edge settings.

### `showMethods()`

**Signature:**

```java
public GraphVizDotFileOptions showMethods()
```

Set method display to `true` and return the same receiver. This empty-input operation is
deterministic, has no checked or unchecked exception contract, and changes no unrelated
state.

**Normal example:** `GraphVizDotFileOptions options = new GraphVizDotFileOptions().showMethods();`

**Edge example:** `hideMethods().showMethods()` must end enabled even when the pair is
called several times in succession.

### `hideMethods()`

**Signature:**

```java
public GraphVizDotFileOptions hideMethods()
```

Set method display to `false`, return the same receiver, and perform no I/O or other
external action. No exception is specified for this zero-argument method.

**Normal example:** `GraphVizDotFileOptions options = new GraphVizDotFileOptions().hideMethods();`

**Edge example:** Repeated calls remain false; hiding methods must not hide fields or
change the method-edge option.

### `showMethodTypeDependencyEdges()`

**Signature:**

```java
public GraphVizDotFileOptions showMethodTypeDependencyEdges()
```

Set method-type dependency-edge display to `true` and return the same receiver. The
operation has no arguments, no external side effects, and no checked or unchecked
exception path.

**Normal example:** `GraphVizDotFileOptions options = new GraphVizDotFileOptions().showMethodTypeDependencyEdges();`

**Edge example:** The edge option is independent of method display: calling
`hideMethods().showMethodTypeDependencyEdges()` leaves method display disabled while
enabling its dependency edges.

### `hideMethodTypeDependencyEdges()`

**Signature:**

```java
public GraphVizDotFileOptions hideMethodTypeDependencyEdges()
```

Set method-type dependency-edge display to `false` and return the same receiver. No
arguments are accepted or required, and no exception or external side effect is part
of the contract.

**Normal example:** `GraphVizDotFileOptions options = new GraphVizDotFileOptions().hideMethodTypeDependencyEdges();`

**Edge example:** Calling this method after `showMethods()` must leave method display
enabled while disabling only method-type dependency edges.

### `showAnnotations()`

**Signature:**

```java
public GraphVizDotFileOptions showAnnotations()
```

Set annotation display to `true`, return the exact receiver, and change no other option.
This zero-argument method is deterministic and has no checked or unchecked exception
path or external side effect.

**Normal example:** `GraphVizDotFileOptions options = new GraphVizDotFileOptions().showAnnotations();`

**Edge example:** Calling `showAnnotations()` repeatedly must not affect annotation
dependency-edge visibility or name rendering.

### `hideAnnotations()`

**Signature:**

```java
public GraphVizDotFileOptions hideAnnotations()
```

Set annotation display to `false` and return the same receiver. It takes no inputs,
performs no external work, and has no specified checked or unchecked exception.

**Normal example:** `GraphVizDotFileOptions options = new GraphVizDotFileOptions().hideAnnotations();`

**Edge example:** `hideAnnotations().showAnnotationDependencyEdges()` must keep
annotation display disabled while enabling its separate edge option.

### `showAnnotationDependencyEdges()`

**Signature:**

```java
public GraphVizDotFileOptions showAnnotationDependencyEdges()
```

Set annotation dependency-edge display to `true` and return the same receiver. There
are no arguments, no checked or unchecked exception path, and no side effect outside
the receiver.

**Normal example:** `GraphVizDotFileOptions options = new GraphVizDotFileOptions().showAnnotationDependencyEdges();`

**Edge example:** Enabling annotation dependency edges must not implicitly enable
annotation display or alter field and method settings.

### `hideAnnotationDependencyEdges()`

**Signature:**

```java
public GraphVizDotFileOptions hideAnnotationDependencyEdges()
```

Set annotation dependency-edge display to `false` and return the same receiver. The
empty input domain has no invalid value, so no checked or unchecked exception is part
of this contract.

**Normal example:** `GraphVizDotFileOptions options = new GraphVizDotFileOptions().hideAnnotationDependencyEdges();`

**Edge example:** Repeating the method must be idempotent and must not change whether
annotations themselves are shown.

### `useSimpleNames()`

**Signature:**

```java
public GraphVizDotFileOptions useSimpleNames()
```

Set name rendering to simple names, return the same receiver, and leave all other
options unchanged. The method takes no arguments and has no checked or unchecked
exception path or external side effect.

**Normal example:** `GraphVizDotFileOptions options = new GraphVizDotFileOptions().useSimpleNames();`

**Edge example:** Calling `useSimpleNames()` after `useFullyQualifiedNames()` must
restore simple-name rendering without resetting layout or visibility choices.

### `useFullyQualifiedNames()`

**Signature:**

```java
public GraphVizDotFileOptions useFullyQualifiedNames()
```

Set name rendering to fully qualified names and return the same receiver. It has no
arguments, no external side effects, and no checked or unchecked exception path.

**Normal example:** `GraphVizDotFileOptions options = new GraphVizDotFileOptions().useFullyQualifiedNames();`

**Edge example:** Calling the method twice remains fully qualified rather than toggling
back to simple names.

### `includeExternalClasses()`

**Signature:**

```java
public GraphVizDotFileOptions includeExternalClasses()
```

Set the external-class choice to explicitly included (`true`) and return the same
receiver. This method takes no arguments, performs no classpath scan, and has no
checked or unchecked exception path in the bounded contract.

**Normal example:** `GraphVizDotFileOptions options = new GraphVizDotFileOptions().includeExternalClasses();`

**Edge example:** Calling it on a fresh instance changes the external-class choice
from unset to explicitly included; it must not change any other default.

### `excludeExternalClasses()`

**Signature:**

```java
public GraphVizDotFileOptions excludeExternalClasses()
```

Set the external-class choice to explicitly excluded (`false`) and return the same
receiver. It takes no arguments, performs no scan or I/O, and has no checked or
unchecked exception path.

**Normal example:** `GraphVizDotFileOptions options = new GraphVizDotFileOptions().excludeExternalClasses();`

**Edge example:** Calling `includeExternalClasses().excludeExternalClasses()` leaves
the explicit choice from the last call, excluded, rather than returning to the initial
unset state.

### Fluent composition

All mutators return the original object, not a copy. A normal composition is:

```java
GraphVizDotFileOptions options = new GraphVizDotFileOptions()
    .setLayoutSize(12.0f, 8.0f)
    .hideFields()
    .hideMethods()
    .useFullyQualifiedNames()
    .excludeExternalClasses();
```

An edge composition is to apply the same pair in both orders. For example,
`showFields().hideFields()` must finish with fields hidden, while
`hideFields().showFields()` must finish with fields shown. The same last-call rule
applies to every show/hide or naming/external-class pair.

## Implementation Notes

Keep the implementation as one public Java class in the exact package shown above.
Use instance state so two objects can be configured independently. The class must not
use static mutable configuration, environment variables, system properties, clocks,
threads, filesystem paths, subprocesses, network clients, reflection, or classpath
scanning. No method should require a third-party library.

Preserve the separation between dimensions and every boolean option. `setLayoutSize`
updates both dimensions but does not touch booleans. A display option does not imply
its related dependency-edge option, and an edge option does not imply display. Name
selection does not affect layout or visibility. External-class selection is the one
tri-state concern: fresh instances leave it unset, and the two explicit methods set
it to their respective values.

The mutator methods are assignments, not toggles. A repeated `show...` call stays true
and a repeated `hide...` call stays false. The final state after a sequence is
determined by the last method in each pair. Preserve the exact float values supplied
to `setLayoutSize`; do not introduce validation or normalization for finite or
non-finite values.

The following small scenarios must be possible to verify without network access:

1. A fresh object has width `10.5f`, height `8.0f`, all listed display/edge choices
   enabled, simple names enabled, and external classes unset.
2. `setLayoutSize(0.0f, -2.0f)` preserves zero and the negative height and returns the
   same object.
3. `hideFields().showFields()` ends with fields enabled while unrelated defaults remain
   unchanged.
4. `showMethods().hideMethodTypeDependencyEdges()` enables method display but disables
   only method-type dependency edges.
5. `useFullyQualifiedNames().useSimpleNames()` ends with simple names selected.
6. `includeExternalClasses().excludeExternalClasses()` ends explicitly excluded, while
   a never-configured instance remains unset for that choice.

Do not copy an upstream implementation, reproduce an algorithm, add behavior inferred
from unrelated ClassGraph modules, or expose verifier protocols and private test
details. The public specification above is the complete confidently bindable API for
this task; no additional public class, method, CLI entry, or module is confidently
bindable from the task-local inventory.
