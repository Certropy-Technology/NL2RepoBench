# Build `exceptiongroup`

Create a complete, installable Python distribution named `exceptiongroup`
from an empty workspace. The project provides the PEP 654 exception-group
backport and compatibility helpers used by libraries that support Python
versions both before and after Python 3.11.

## Project Description

The import package is `exceptiongroup`. On Python 3.11 and newer it re-exports
the native `BaseExceptionGroup` and `ExceptionGroup` classes, while retaining
portable helpers for handling, suppressing, and formatting exception groups.
On older supported Python versions it provides compatible pure-Python group
classes and traceback formatting support. The evaluation runtime is CPython
3.12, but the source layout and metadata must remain a genuine backport
package rather than a module that only works inside the evaluator.

The distribution version is `1.3.1.post6`, matching the frozen source
revision. The package is typed and includes `exceptiongroup/py.typed`.

## Supports

- Support Python 3.7 and newer Python 3 versions. The evaluation runtime is
  CPython 3.12.
- Provide a normal PEP 517 installable project. A Flit/Flit-SCM build or an
  equivalent build backend with static version metadata is acceptable.
- Declare `typing-extensions >= 4.6.0` when `python_version < "3.13"`; there
  are no other runtime dependencies.
- Keep normal behavior deterministic and local. Importing and using the
  package must not access the network, run external commands, or depend on a
  service.
- Preserve the public root API, compatibility submodules, exception context,
  traceback, notes, and nested group shape described below.
- On Python 3.11 and newer, importing `exceptiongroup` must not monkeypatch
  `traceback.TracebackException` or replace `sys.excepthook`.

## API Usage Guide

### Root exports

`exceptiongroup.__all__` is this ordered list:

```text
BaseExceptionGroup, ExceptionGroup, catch, format_exception,
format_exception_only, print_exception, print_exc, suppress
```

All eight names are importable from the package root. The root also exposes
`__version__ == "1.3.1.post6"`. These compatibility modules remain
importable: `exceptiongroup._catch`, `exceptiongroup._exceptions`,
`exceptiongroup._formatting`, and `exceptiongroup._suppress`.

On Python 3.11 and newer, the two group classes are the corresponding built-in
classes. On older Python versions, the backported classes follow the PEP 654
data model: `ExceptionGroup` derives from both `BaseExceptionGroup` and
`Exception`, while `BaseExceptionGroup` derives from `BaseException`.

### Exception-group construction and methods

The public constructors are:

```python
BaseExceptionGroup(message: str, exceptions: Sequence[BaseException])
ExceptionGroup(message: str, exceptions: Sequence[Exception])
```

The message must be a string and the exception sequence must be non-empty.
Every member must be an exception instance. Constructing
`BaseExceptionGroup` with only ordinary `Exception` instances returns an
`ExceptionGroup`. `ExceptionGroup` rejects `BaseException` members such as
`KeyboardInterrupt`.

Instances expose read-only `message` and `exceptions` properties. The latter
is a stable tuple snapshot, so later mutation of the input sequence does not
change the group or its representation. `str(group)` reports the message and
sub-exception count. `add_note(text)` accepts strings and appends to
`__notes__`.

The group operations are:

```python
group.subgroup(condition) -> BaseExceptionGroup | None
group.split(condition) -> tuple[BaseExceptionGroup | None,
                                BaseExceptionGroup | None]
group.derive(exceptions) -> BaseExceptionGroup
```

`condition` is an exception class, a tuple of exception classes, or a
predicate callable. `subgroup()` recursively retains matching leaves;
`split()` returns matching and nonmatching groups. Both preserve nesting and
leaf order. Derived groups copy the original cause, context, traceback, and a
separate copy of notes. A subclass can override `derive()` to preserve custom
state.

### `catch`

```python
catch(handlers: Mapping[
    type[BaseException] | Iterable[type[BaseException]],
    Callable[[BaseExceptionGroup], object],
]) -> AbstractContextManager[None]
```

`catch()` returns a synchronous context manager. Each key is one exception
class or an iterable of classes; each value is a callable handler. When the
body raises, every handler is invoked at most once with the recursively
matching subgroup. Handler order follows mapping order. Fully handled leaves
are suppressed and unmatched leaves are reraised with their nested shape and
chaining preserved. A naked matching exception is wrapped into a one-leaf
group for its handler.

The argument must be a mapping, handlers must be callable, and key members
must be exception classes. `BaseExceptionGroup` and `ExceptionGroup` cannot
be handler keys. A handler returning a coroutine is rejected with `TypeError`;
handlers are synchronous. Exceptions raised by handlers propagate with the
original group as context, while a bare reraise retains the matching group.

### `suppress`

```python
suppress(*exceptions: type[BaseException])
```

This is compatible with `contextlib.suppress`. It suppresses matching naked
exceptions. For an exception group it recursively removes matching leaves;
if all leaves match, the whole group is suppressed, otherwise the derived
remainder is raised with its original nesting. On Python 3.12.1 and newer the
root export may be the standard-library implementation; the compatibility
module remains importable.

### Traceback helpers

These root functions follow their `traceback` counterparts and support both
modern and legacy call forms where applicable:

```python
format_exception(exc, limit=None, chain=True, **kwargs) -> list[str]
format_exception(exc_type, value, traceback, limit=None, chain=True,
                 **kwargs) -> list[str]
format_exception_only(exc, **kwargs) -> list[str]
format_exception_only(exc_type, value, **kwargs) -> list[str]
print_exception(exc, limit=None, file=None, chain=True, **kwargs) -> None
print_exception(exc_type, value, traceback, limit=None, file=None,
                chain=True) -> None
print_exc(limit=None, file=None, chain=True) -> None
```

Formatting returns newline-terminated strings and includes exception-group
messages, nested leaf types/messages, causes or contexts when `chain=True`,
and attached notes. Printing writes the same information to `file` or to
standard error. `print_exc()` formats the currently handled exception.

## Implementation Notes

Preserve exception object identity where PEP 654 requires it, but create new
derived group containers when only part of a group matches. Do not flatten
nested groups. Copy notes rather than sharing a mutable note list between
derived groups.

Code for the older-Python backport may adapt standard-library behavior, but
the evaluator must be able to install the project from a source tree without
Git metadata. Make version generation deterministic in that case. Do not
retrieve the upstream repository, tests, or a preinstalled implementation at
runtime.
