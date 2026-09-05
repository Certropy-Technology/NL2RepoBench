# Project Description

Build the pure-Python `typing-inspection` package from an empty workspace. The
package provides runtime predicates for objects from `typing` and
`typing_extensions`, plus higher-level annotation inspection that consistently
handles unions, literals, qualifiers, metadata, and version-dependent typing
objects.

Target package metadata:

- Distribution: `typing-inspection`
- Import package: `typing_inspection`
- Version: `0.4.4`
- Python: `>=3.10`
- Runtime dependency: `typing-extensions>=4.15.0`
- Typed marker: include `typing_inspection/py.typed`

# Natural Language Instruction

Create the pure-Python `typing-inspection` package from an empty workspace.
Implement runtime typing predicates and annotation inspection for the standard
`typing` and `typing_extensions` forms described below. Preserve qualifier
validation, metadata order, alias modes, and deterministic behavior.

# Supports

The implementation must provide these import modules:

- `typing_inspection`
- `typing_inspection.introspection`
- `typing_inspection.typing_objects`

The root package does not need to re-export the child modules' members. Public
behavior must work on CPython 3.12 and remain compatible with Python 3.10 and
newer. Results are deterministic and perform no I/O, network access, logging,
or mutation of caller-owned objects.

The package must recognize matching objects from both `typing` and
`typing_extensions` where both expose a form. Identity checks must not
misclassify arbitrary objects or instances.

# Project Directory Structure

```text
workspace/
├── pyproject.toml
└── typing_inspection/
    ├── __init__.py
    ├── introspection.py
    ├── typing_objects.py
    └── py.typed
```

# API Usage Guide

## `typing_inspection.introspection`

### Union origins

```python
def is_union_origin(obj: Any, /) -> bool: ...
```

Return whether `obj` is an origin representing a union. On Python versions
before 3.14 this includes both `typing.Union` and `types.UnionType`; ordinary
types return `False`.

```python
from typing import get_origin
from typing_inspection.introspection import is_union_origin

assert is_union_origin(get_origin(int | str))
assert not is_union_origin(int)
```

### Literal values

```python
def get_literal_values(
    annotation: Any,
    /,
    *,
    type_check: bool = False,
    unpack_type_aliases: Literal["skip", "lenient", "eager"] = "eager",
) -> Generator[Any]: ...
```

Yield values in a `typing.Literal` form in declaration order. Treat `None` and
`type(None)` as equivalent and yield a single `None`. Preserve duplicate
unhashable values rather than failing while deduplicating.

When `type_check=True`, legal literal values are integers, bytes, strings,
booleans, enum members, `None`, and `type(None)`; an illegal value raises
`TypeError` with a useful value-and-domain message.

`unpack_type_aliases` controls PEP 695 aliases:

- `"skip"` yields an alias without resolving it.
- `"lenient"` resolves it when possible and leaves it intact if evaluating its
  value raises `NameError`.
- `"eager"` resolves it recursively and propagates `NameError`.

```python
from typing import Literal
from typing_inspection.introspection import get_literal_values

assert list(get_literal_values(Literal[1, "x", None])) == [1, "x", None]
```

### Qualifier model

```python
Qualifier: TypeAlias = Literal[
    "required", "not_required", "read_only", "class_var", "init_var", "final"
]
```

```python
class AnnotationSource(IntEnum):
    ASSIGNMENT_OR_VARIABLE = 1
    CLASS = 2
    DATACLASS = 3
    TYPED_DICT = 4
    NAMED_TUPLE = 5
    FUNCTION = 6
    ANY = 7
    BARE = 8

    @property
    def allowed_qualifiers(self) -> set[Qualifier]: ...
```

Allowed qualifiers are:

| Source | Allowed qualifiers |
| --- | --- |
| `ASSIGNMENT_OR_VARIABLE` | `final` |
| `CLASS` | `class_var`, `final` |
| `DATACLASS` | `class_var`, `final`, `init_var` |
| `TYPED_DICT` | `required`, `not_required`, `read_only` |
| `NAMED_TUPLE`, `FUNCTION`, `BARE` | none |
| `ANY` | all qualifiers |

The returned sets are ordinary mutable sets owned by the caller.

```python
class ForbiddenQualifier(Exception):
    qualifier: Qualifier
    def __init__(self, qualifier: Qualifier, /) -> None: ...
```

Raise this exception when an annotation contains a qualifier not allowed by
its `AnnotationSource`. The offending qualifier is available as `.qualifier`.

`UNKNOWN` is a singleton sentinel used when a bare `Final`, `ClassVar`, or
`InitVar` has no underlying type expression. `str(UNKNOWN)` is `"UNKNOWN"` and
`repr(UNKNOWN)` is `"<UNKNOWN>"`.

```python
class InspectedAnnotation(NamedTuple):
    type: Any
    qualifiers: set[Qualifier]
    metadata: list[Any]
```

The `type` field is the stripped type expression or `UNKNOWN`. `qualifiers`
contains all discovered qualifiers without duplicates. `metadata` preserves
the inner-to-outer order of `Annotated` metadata.

```python
def inspect_annotation(
    annotation: Any,
    /,
    *,
    annotation_source: AnnotationSource,
    unpack_type_aliases: Literal["skip", "lenient", "eager"] = "skip",
) -> InspectedAnnotation: ...
```

Strip nested `Annotated` metadata and supported type qualifiers until reaching
the underlying type expression. PEP 695 alias modes have the same meanings as
for `get_literal_values`. Invalid source/qualifier combinations raise
`ForbiddenQualifier`; eager evaluation of an unresolved alias may raise
`NameError`.

```python
from typing import Annotated
from typing_extensions import ClassVar, Final
from typing_inspection.introspection import AnnotationSource, inspect_annotation

item = inspect_annotation(
    Final[Annotated[ClassVar[Annotated[int, "inner"]], "outer"]],
    annotation_source=AnnotationSource.CLASS,
)
assert item.type is int
assert item.qualifiers == {"class_var", "final"}
assert item.metadata == ["inner", "outer"]
```

## `typing_inspection.typing_objects`

All predicates below accept one positional-only object and return `bool`. The
`TypeIs` return annotations shown for narrowing predicates are part of the
typing contract; runtime values are still booleans. None of these functions
raise for arbitrary ordinary objects.

```python
def is_annotated(obj: Any, /) -> bool: ...
def is_any(obj: Any, /) -> bool: ...
def is_classvar(obj: Any, /) -> bool: ...
def is_concatenate(obj: Any, /) -> bool: ...
def is_final(obj: Any, /) -> bool: ...
def is_generic(obj: Any, /) -> bool: ...
def is_literal(obj: Any, /) -> bool: ...
def is_literalstring(obj: Any, /) -> bool: ...
def is_never(obj: Any, /) -> bool: ...
def is_nodefault(obj: Any, /) -> bool: ...
def is_noextraitems(obj: Any, /) -> bool: ...
def is_noreturn(obj: Any, /) -> bool: ...
def is_notrequired(obj: Any, /) -> bool: ...
def is_readonly(obj: Any, /) -> bool: ...
def is_required(obj: Any, /) -> bool: ...
def is_self(obj: Any, /) -> bool: ...
def is_typealias(obj: Any, /) -> bool: ...
def is_typeguard(obj: Any, /) -> bool: ...
def is_typeis(obj: Any, /) -> bool: ...
def is_union(obj: Any, /) -> bool: ...
def is_unpack(obj: Any, /) -> bool: ...
```

These identify their same-named special typing forms. Before Python 3.14,
`is_union(types.UnionType)` is `False`; use `is_union_origin` when both union
syntaxes must be accepted as origins.

```python
def is_forwardref(obj: Any, /) -> TypeIs[ForwardRef]: ...
def is_paramspec(obj: Any, /) -> TypeIs[ParamSpec]: ...
def is_paramspecargs(obj: Any, /) -> TypeIs[ParamSpecArgs]: ...
def is_paramspeckwargs(obj: Any, /) -> TypeIs[ParamSpecKwargs]: ...
def is_typevar(obj: Any, /) -> TypeIs[TypeVar]: ...
def is_typevartuple(obj: Any, /) -> TypeIs[TypeVarTuple]: ...
def is_typealiastype(obj: Any, /) -> TypeIs[TypeAliasType]: ...
def is_deprecated(obj: Any, /) -> TypeIs[deprecated]: ...
```

These identify runtime instances of the corresponding constructor or marker
class. `is_deprecated` accepts a marker created by
`typing_extensions.deprecated("message")`, not the factory itself.

```python
def is_namedtuple(obj: Any, /) -> bool: ...
def is_newtype(obj: Any, /) -> TypeIs[NewType]: ...
```

`is_namedtuple` accepts named-tuple classes created through `typing.NamedTuple`,
`typing_extensions.NamedTuple`, or `collections.namedtuple`, but rejects their
instances and plain `tuple`. `is_newtype` accepts the object returned by
`typing.NewType`, but rejects its converted values and normal classes.

```python
NoneType: type[None]
DEPRECATED_ALIASES: Final[dict[Any, type[Any]]]
DEPRECATED_ALIASES_IDS: Final[dict[int, type[Any]]]
```

`NoneType` is `type(None)`. `DEPRECATED_ALIASES` maps supported deprecated
`typing` aliases to their replacement runtime classes, such as `typing.List`
to `list`, `typing.Dict` to `dict`, `typing.Pattern` to `re.Pattern`, and
`typing.Match` to `re.Match`. `DEPRECATED_ALIASES_IDS` provides the same lookup
by `id(alias)` for aliases that cannot be used reliably as equality keys.

# Implementation Notes

- Use a standard Python project layout that can be installed with
  `pip install --no-build-isolation .` from the workspace root.
- Include complete distribution metadata and the `py.typed` marker.
- `typing_objects` may use a `.pyi` public surface backed by a Python runtime
  implementation, as long as imports and runtime behavior match the API above.
- Account for Python-version identity differences between `typing`,
  `types.UnionType`, and `typing_extensions` without importing private test
  material.
- Do not access the network, inspect external source trees, or depend on the
  current working directory at runtime.

# Examples

```python
from typing import Literal
from typing_inspection.introspection import get_literal_values

assert list(get_literal_values(Literal[1, "x"])) == [1, "x"]
```

```python
from typing import Annotated
from typing_extensions import Final
from typing_inspection.introspection import AnnotationSource, inspect_annotation

result = inspect_annotation(Final[Annotated[int, "meta"]],
                            annotation_source=AnnotationSource.ASSIGNMENT_OR_VARIABLE)
assert result.type is int
```

# Error Handling and Boundary Conditions

Predicates return `False` for unrelated objects rather than raising. Invalid
qualifier/source combinations raise `ForbiddenQualifier`; eager unresolved
aliases may raise `NameError`. Metadata order and duplicate elimination follow
the API contract, including unhashable literal values.
