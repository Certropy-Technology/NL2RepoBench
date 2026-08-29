# Public API inventory

Frozen source: `python/mypy_extensions` commit
`9fc7fe08c8e638cdd9bbf1aa9bf188aef4fd24ef`.

The implementation is the single module `mypy_extensions.py`. The intended
public runtime surface is derived from the source documentation, upstream
tests, and non-underscore definitions rather than from `__all__`, which the
module does not define.

| Public name | Runtime shape | Observable contract |
| --- | --- | --- |
| `Arg` | function `(type=Any, name=None)` | returns `type` unchanged |
| `DefaultArg` | function `(type=Any, name=None)` | returns `type` unchanged |
| `NamedArg` | function `(type=Any, name=None)` | returns `type` unchanged |
| `DefaultNamedArg` | function `(type=Any, name=None)` | returns `type` unchanged |
| `VarArg` | function `(type=Any)` | returns `type` unchanged |
| `KwArg` | function `(type=Any)` | returns `type` unchanged |
| `TypedDict` | metaclass-backed factory/base | deprecated functional and class forms; plain-dict instances and metadata |
| `trait` | function `(cls)` | identity decorator |
| `mypyc_attr` | function `(*attrs, **kwattrs)` | returns an identity decorator |
| `FlexibleAlias` | subscriptable singleton | retains `subscription_arguments[-1]` from the first stage and returns it from second-stage subscriptions |
| `i64` | class `(x=0, base=<sentinel>)` | built-in `int` conversion and `int` instance checks |
| `i32` | class `(x=0, base=<sentinel>)` | built-in `int` conversion and `int` instance checks |
| `i16` | class `(x=0, base=<sentinel>)` | built-in `int` conversion and `int` instance checks |
| `u8` | class `(x=0, base=<sentinel>)` | built-in `int` conversion and `int` instance checks |
| `NoReturn` | dynamic module attribute | deprecated compatibility marker, cached after first access |

`Any` and `Dict` are imported implementation dependencies from `typing`, and
`sys` is an imported standard-library module. Their incidental module
visibility is not part of this task's required public API.

Private helpers include `_check_fails`, `_dict_new`, `_typeddict_new`,
`_TypedDictMeta`, `_DEPRECATED_NoReturn`, `_FlexibleAliasClsApplied`,
`_FlexibleAliasCls`, `_NativeIntMeta`, `_sentinel`, and `_warn_deprecation`.
Candidate implementations may organize private code differently.

## Stateful and non-JSON boundaries

The following behaviors cannot be faithfully tested by directly serializing
API arguments or results:

- class and type identity;
- metaclass-driven `isinstance`/`issubclass` behavior;
- caller module metadata and inheritance;
- warnings;
- pickling of module-bound classes;
- decorators preserving exact object identity; and
- `typing` expressions containing generated classes.

The private verifier therefore sends behavior-only scenario programs to the
standard UID-separated candidate runner. Expected values and grading remain in
the trusted parent verifier. Candidate code is never added to the trusted
process's `sys.path`.
