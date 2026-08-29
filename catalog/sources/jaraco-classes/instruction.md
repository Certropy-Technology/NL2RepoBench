# Build `jaraco.classes`

Create a complete, installable Python project named `jaraco.classes` from an
empty workspace. The project is a small pure-Python utility package for class
introspection, descriptors, and metaclass registries. The implementation must
match the public behavior described here without copying the frozen reference
source or relying on network access at runtime.

## Project Description

The package provides three focused modules under the `jaraco.classes` import
package. `ancestry` exposes deterministic class hierarchy helpers,
`properties` provides reusable descriptor implementations, and `meta` provides
metaclasses for tracking leaf classes and registering tagged classes. The
package is intentionally local and has no command line interface or service
integration.

## Supports

- Support CPython 3.10 or newer Python 3.x versions in the supported source
  range, using a normal `src/` or package-root layout.
- Install the distribution named `jaraco.classes` with a standard PEP 517
  build backend. A source checkout is not available during candidate install,
  so package version metadata must be deterministic without setuptools SCM
  state.
- Import `jaraco.classes.ancestry`, `jaraco.classes.meta`, and
  `jaraco.classes.properties` from an empty workspace after installation.
- Declare `more_itertools` as the only runtime dependency. It is used by
  `iter_subclasses`; do not replace the dependency with a network lookup or a
  vendored wheel.
- Include the `jaraco/classes/py.typed` marker and keep runtime behavior free
  of subprocesses, network calls, and external services.
- Preserve declaration order where a class hierarchy or registry promises it.
  Do not make scored results depend on hash iteration order or memory
  addresses.

## API Usage Guide

### `jaraco.classes.ancestry`

```python
all_bases(c: type[object]) -> list[type[object]]
all_classes(c: type[object]) -> list[type[object]]
iter_subclasses(cls: type[object]) -> Iterator[type[object]]
```

`all_bases` returns `c.mro()[1:]` and `all_classes` returns `c.mro()`, both as
new lists. `iter_subclasses` yields descendants depth-first: each direct child
is yielded before recursively visiting its descendants, and the same class is
yielded at most once even when a diamond hierarchy reaches it through multiple
paths. Direct subclasses retain Python's declaration order. The helper must
also work for `type`, whose `__subclasses__` call needs the normal Python
special case.

### `jaraco.classes.properties.NonDataProperty`

```python
NonDataProperty(fget: Callable[[object], object])
NonDataProperty.__get__(obj, objtype=None)
```

This is a non-data descriptor: its constructor rejects a missing or
non-callable getter with `AssertionError`, and stores the getter as `fget`.
Access through the class returns the descriptor itself. Access through an
instance calls `fget(instance)`. Because it has no `__set__`, assigning an
instance attribute with the same name shadows the descriptor for that
instance and the value remains in the instance dictionary.

### `jaraco.classes.properties.classproperty`

```python
classproperty(fget, fset=None)
classproperty.setter(fset) -> classproperty
classproperty.Meta
```

`classproperty` evaluates its getter with the owning class and works through
both the class and an instance. The getter may be an ordinary function,
`classmethod`, or `staticmethod`; ordinary functions are bound as class
methods. `@prop.setter` installs a setter and returns the same descriptor.

Use `classproperty.Meta` as the metaclass when class assignment must be
intercepted. The metaclass recognizes a descriptor stored directly in the
class dictionary and routes `Class.prop = value` to its setter. On an instance,
the descriptor similarly routes assignment to that instance's type. A class
that does not use `classproperty.Meta` retains Python's legacy behavior:
instance assignment can shadow the descriptor, while class assignment replaces
the descriptor as a normal class attribute operation.

### `jaraco.classes.meta.LeafClassesMeta`

```python
class LeafClassesMeta(type):
    _leaf_classes: set[type[object]]
```

Every class created with this metaclass participates in a registry named
`_leaf_classes`. The registry is shared by a base and its descendants. A newly
created class is added and all of its direct base classes are removed, so the
registry contains the current leaves. Independent metaclass hierarchies each
start with their own registry. The set is intentionally a set; callers should
sort names when a stable display is required.

### `jaraco.classes.meta.TagRegistered`

```python
class TagRegistered(type):
    attr_name = "tag"
    _registry: dict[object, type[object]]
```

Classes created with `TagRegistered` share an inherited `_registry` with their
base hierarchy. If the newly created class has a truthy attribute named by the
metaclass's `attr_name`, the value is registered to that class. A child with a
new tag adds a new entry; a repeated tag replaces the previous entry. A class
without a truthy tag does not add an entry. Independent roots have independent
registries. Registry operations must not make class creation depend on network
or filesystem state.

### Package files and metadata

The import package must include `jaraco/classes/__init__.py`, the three modules
above, and `jaraco/classes/py.typed`. The root package need not re-export the
module contents. The installed distribution name must be `jaraco.classes`,
must have a deterministic version, and must declare `more_itertools` without
pulling dependencies during the evaluation run.

## Implementation Notes

Keep the implementation modular and preserve the public import paths and
exception behavior. Descriptor ownership, class-vs-instance binding, and
metaclass initialization are observable Python data-model protocols, so use
ordinary descriptors and metaclasses rather than a look-alike helper API.

The frozen upstream revision contains doctest examples but no tracked pytest
suite. The task therefore uses a fixed, private, deterministic custom-json
verification contract covering the public behaviors above. Do not add upstream
tests, source archives, verifier code, or reference implementation text to
the candidate project.

Runtime package behavior must remain deterministic for fixed class definitions
and values. It is acceptable for ordinary object reprs, hash values, and
implementation-specific typing details to vary; the scored contract compares
only explicit values, class names, registry membership, exception types, and
stable descriptor behavior.
