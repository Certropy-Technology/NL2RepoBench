# Project Description

Build an installable Python distribution named `jaraco.classes` from an empty
workspace. The project is a small class-introspection toolkit with ancestry
helpers, non-data and class-level descriptors, and metaclass registries. It is
local pure-Python behavior: no command-line service, network access, or
external state is required.

# Natural Language Instruction

Create the package so an installed `jaraco.classes` distribution exposes the
`ancestry`, `properties`, and `meta` modules. Implement deterministic class
hierarchy traversal, descriptor binding and shadowing, classproperty setters,
leaf-class tracking, and tag registration. Preserve the public names,
declaration order where promised, and normal Python exceptions. Include typed
package metadata and an installable build configuration; do not copy an
upstream checkout or tests.

# Supports or Environment Configuration

- Use CPython 3.10 or newer; the evaluation runtime is Python 3.12 on Linux.
- Distribution name: `jaraco.classes`; import package: `jaraco.classes`.
- Install from the workspace with a normal PEP 517 build and the preinstalled
  build environment. Declare `more_itertools` as the only runtime dependency.
- Include a deterministic package version without requiring VCS metadata.
- Runtime behavior must not use subprocesses, network services, current time,
  or user-specific files. Agent, candidate, verifier, Oracle, and controls run
  with no network access; dependencies are prepared before the run.

# Project Directory Structure

```text
workspace/
├── pyproject.toml
├── README.md
├── LICENSE
└── jaraco/
    ├── __init__.py
    └── classes/
        ├── __init__.py
        ├── py.typed
        ├── ancestry.py
        ├── meta.py
        └── properties.py
```

# API Usage Guide

## `jaraco.classes.ancestry`

```python
all_bases(c: type[object]) -> list[type[object]]
all_classes(c: type[object]) -> list[type[object]]
iter_subclasses(cls: type[object]) -> Iterator[type[object]]
```

`all_bases` returns a new list containing `c.mro()[1:]`; `all_classes` returns
the complete MRO as a new list. `iter_subclasses` yields descendants
depth-first, yielding each direct child before its descendants and never
yielding a class twice through a diamond. Direct subclass order follows Python
declaration order. The `type` root must work as well.

## `jaraco.classes.properties`

```python
NonDataProperty(fget: Callable[[object], object])
NonDataProperty.__get__(obj, objtype=None)
classproperty(fget, fset=None)
classproperty.setter(fset) -> classproperty
```

`NonDataProperty` rejects a missing or non-callable getter with
`AssertionError`. Class access returns the descriptor; instance access calls
the getter. Because it has no setter, an instance attribute with the same name
shadows it. `classproperty` evaluates its getter with the owning class,
regardless of class or instance access. Ordinary functions, `classmethod`, and
`staticmethod` getters are accepted. Its `setter` decorator returns the same
descriptor. With `classproperty.Meta` as metaclass, assignment through a class
or instance invokes the setter; without that metaclass, ordinary legacy class
assignment behavior remains.

## `jaraco.classes.meta`

```python
class LeafClassesMeta(type): ...
class TagRegistered(type): ...
```

`LeafClassesMeta._leaf_classes` is shared within one metaclass hierarchy. A
new class is added and its direct bases are removed, leaving current leaves;
independent roots have independent sets. `TagRegistered.attr_name` defaults
to `"tag"`, and `_registry` is inherited within one root. A truthy tag on a
new class registers that class; a duplicate tag replaces the prior entry and a
missing/false tag changes nothing. Registry operations are deterministic for
fixed class definitions.

## Package contract

The package must expose the modules above, include `jaraco/classes/py.typed`,
and remain importable from its installed target. The public contract includes
the descriptor ownership rules and the exact registry membership behavior, not
the names of private helpers.

# Implementation Notes

Use ordinary Python descriptors and metaclasses so class-vs-instance binding,
attribute shadowing, and class construction follow the data model. Return new
lists for MRO functions and do not expose mutable registry state through an
undocumented alternate API. Use deterministic traversal and sort a set only
when presenting it; the registry itself is intentionally a set for leaf
classes.

# Examples

```python
from jaraco.classes.ancestry import all_bases, iter_subclasses

class Root: pass
class Child(Root): pass

assert all_bases(Child) == [Root, object]
assert list(iter_subclasses(Root)) == [Child]
```

```python
from jaraco.classes.properties import NonDataProperty, classproperty

class Item:
    value = NonDataProperty(lambda self: 3)

item = Item()
assert item.value == 3
item.value = 4
assert item.value == 4
```

# Error Handling and Boundary Conditions

The task id is `jaraco-classes`; the distribution is `jaraco.classes`.

- A non-callable `NonDataProperty` getter raises `AssertionError` at
  construction.
- A diamond hierarchy must not duplicate a shared descendant.
- A `classproperty` without a setter raises `AttributeError` when assignment is
  routed through `classproperty.Meta`.
- False or absent tags do not enter `TagRegistered._registry`; independent
  roots must not share registry entries.
- Do not rely on hash iteration order, filesystem paths, external services, or
  a preinstalled copy of the package.
