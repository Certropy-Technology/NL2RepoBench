# Project Description

Build `six` 1.17.0, a single-module Python compatibility library. The repository
must be installable from its root and expose the public `six` module plus the
lazy `six.moves` package. This task targets the Python 3 behavior of the API on
CPython 3.12; Python 2 does not need to be available in the execution
environment.

# Supports

- Python 3.12 on 64-bit Linux.
- Root installation with `pip`. The distribution is named `six`, its version is
  `1.17.0`, and it has no runtime dependencies.
- A top-level `six.py` module. Importing it must also make `six` act as a package
  so imports such as `six.moves.queue`, `six.moves.urllib_parse`, and
  `six.moves.urllib.parse` work.
- Deterministic, local behavior only. The module must not require network access
  or external services.

# API Usage Guide

## Version and type constants

On Python 3.12, `six.__version__` is `"1.17.0"`; `PY2`, `PY3`, and `PY34` are
respectively `False`, `True`, and `True`. `string_types`, `integer_types`, and
`class_types` are the one-item tuples `(str,)`, `(int,)`, and `(type,)`.
`text_type` is `str`, `binary_type` is `bytes`, and `MAXSIZE` is
`sys.maxsize`. The module and its `moves` object expose empty `__path__` values
so Python treats both as packages for import purposes.

## Binary and text helpers

`b(data: str) -> bytes` encodes the input with Latin-1. `u(text: str) -> str`
returns text unchanged. `unichr(codepoint: int) -> str` returns the Unicode
character. `int2byte(value: int) -> bytes` accepts values from 0 through 255 and
returns one byte; an out-of-range value raises `struct.error`.

`byte2int(data: bytes) -> int` returns the first byte as an integer and raises
`IndexError` for empty input. `indexbytes(data: bytes, index: int) -> int`
returns the indexed byte as an integer. `iterbytes(data: bytes) -> Iterator[int]`
iterates byte values as integers.

`ensure_binary(value, encoding="utf-8", errors="strict") -> bytes` returns
bytes unchanged and encodes text. `ensure_str(...) -> str` and
`ensure_text(...) -> str` return text unchanged and decode bytes. Each function
passes `encoding` and `errors` to the corresponding codec operation. Values
that are neither text nor bytes raise `TypeError`, and codec errors propagate.

`StringIO` aliases `io.StringIO` and accepts text. `BytesIO` aliases
`io.BytesIO` and accepts bytes. Writing bytes to `StringIO` raises `TypeError`.

## Mapping, iterator, and callable helpers

`iterkeys(mapping, **kwargs)`, `itervalues`, and `iteritems` return iterators
over the corresponding mapping methods and forward keyword arguments.
`iterlists(mapping, **kwargs)` does the same for a mapping's `lists` method.
`viewkeys`, `viewvalues`, and `viewitems` return live mapping views.

`next(iterator)` and `advance_iterator(iterator)` are the same callable. They
return the next item and raise `StopIteration` after exhaustion. `Iterator` is
a portable base class whose subclasses implement `__next__`. `callable(value)`
has the same boolean behavior as the Python built-in.

## Function and method accessors

- `get_unbound_function(method)` returns the underlying function where the
  runtime has unbound methods; on Python 3 it returns the function unchanged.
- `get_method_function(bound_method)` and `get_method_self(bound_method)` return
  `__func__` and `__self__`. Non-method inputs raise `AttributeError`.
- `get_function_closure(function)`, `get_function_code(function)`,
  `get_function_defaults(function)`, and `get_function_globals(function)`
  return the corresponding closure tuple, code object, defaults tuple, and
  globals mapping.
- `create_bound_method(function, instance)` returns a `types.MethodType` bound
  to the instance. `create_unbound_method(function, cls)` returns the original
  function on Python 3, so it still requires an explicit instance argument.

## Execution, printing, and exceptions

`exec_(code, globals=None, locals=None)` executes strings or code objects. With
one namespace it is used for both globals and locals; with two namespaces,
`global` assignments go to the first and ordinary local assignments go to the
second.

`print_(*values, file=sys.stdout, sep=" ", end="\n", flush=False)` follows the
Python 3 `print` contract, including custom separators/endings and flushing.
Non-string `sep` or `end` values raise `TypeError`.

`reraise(exc_type, exc_value, exc_traceback=None)` raises the supplied exception
value with the supplied traceback when present, preserving the exception
object. `raise_from(value, from_value)` implements `raise value from
from_value`; passing `None` as the source sets `__cause__` to `None`, preserves
the active exception as `__context__`, and suppresses display of that context.

## Metaclasses and decorators

`with_metaclass(meta, *bases)` returns a temporary base for a class declaration.
The resulting class uses `meta`, has exactly the requested bases, and calls the
metaclass's `__prepare__` with the final class name and requested bases. On
Python 3.7 and newer it honors `__mro_entries__` and preserves `__orig_bases__`
when bases are resolved.

`add_metaclass(meta)` decorates a class by rebuilding it with `meta` while
preserving its name, module, docstring, qualified name, bases, class attributes,
and `__slots__` behavior. It must not accidentally add an instance dictionary
to a class that only declares slots.

`python_2_unicode_compatible(cls)` returns the class unchanged on Python 3. A
class defining `__str__` and `__bytes__` therefore keeps those methods.

`wraps(wrapped, assigned=..., updated=...)` follows `functools.wraps`: assigned
attributes are copied, updated mappings are merged, and `__wrapped__` references
the wrapped callable. A name listed in `updated` must exist on the wrapper;
otherwise decoration raises `AttributeError`.

## unittest compatibility aliases

`assertCountEqual(test_case, ...)`, `assertRaisesRegex`, `assertRegex`, and
`assertNotRegex` delegate to the corresponding Python 3 `unittest.TestCase`
methods. They preserve normal success behavior and raise `AssertionError` on a
failed assertion.

## `six.moves`

`six.moves` is a lazy module and package. The following Python 3 mappings are
required:

| Move | Python 3 target |
| --- | --- |
| `builtins` | `builtins` |
| `cPickle` | `pickle` |
| `collections_abc` | `collections.abc` |
| `configparser` | `configparser` |
| `html_parser` | `html.parser` |
| `queue` | `queue` |
| `filter` | `builtins.filter` |
| `filterfalse` | `itertools.filterfalse` |
| `map` | `builtins.map` |
| `range` and `xrange` | `builtins.range` |
| `reduce` | `functools.reduce` |
| `zip` | `builtins.zip` |
| `zip_longest` | `itertools.zip_longest` |

Moved modules support both attribute imports and module imports. For example,
`from six.moves.queue import Queue` works, and the imported module is the real
`queue` module. The required names appear in `dir(six.moves)`.

`six.moves.urllib` supplies `parse`, `error`, `request`, `response`, and
`robotparser`. The underscore forms `urllib_parse`, `urllib_error`,
`urllib_request`, `urllib_response`, and `urllib_robotparser` are also
available. Direct imports through `six.moves.urllib.parse` and
`six.moves.urllib_parse` resolve through the lazy import protocol and expose the
standard Python 3 URL parsing, quoting, joining, request, response, and error
objects.

## Custom moves

`MovedModule(name, old_mod, new_mod=None)` and
`MovedAttribute(name, old_mod, new_mod, old_attr=None, new_attr=None)` describe
lazy mappings. On Python 3, the new module/name is selected; omitted attribute
names fall back to the old attribute and then to the move name.

`add_move(move)` registers a descriptor on `six.moves`. Accessing it lazily
returns the chosen module or attribute. `remove_move(name)` removes either an
unresolved descriptor or a resolved cached value. Removing an unknown name
raises `AttributeError`.

# Implementation Notes

- Keep candidate imports isolated to the installed candidate module; do not
  depend on another copy of `six` from the environment.
- The lazy importer must provide stable module specs for direct and nested
  `six.moves` imports, including repeated imports.
- Preserve iterator laziness and live mapping-view behavior rather than
  returning eagerly materialized lists.
- No behavior in this contract requires external data, a subprocess service, or
  network access.
