# Public Contract Traceability

| Public contract area | Upstream authority | Verifier coverage |
| --- | --- | --- |
| Ordered root exports, version and compatibility modules | `src/exceptiongroup/__init__.py`, package metadata | exports, metadata, submodule and marker leaves |
| Group construction, hierarchy, tuple snapshot and representation | `_exceptions.py`, `test_exceptions.py` | construction, validation, fields, repr and generics leaves |
| Recursive `split`, `subgroup`, derived attributes and subclass state | `_exceptions.py`, `test_exceptions.py` | split/subgroup/attribute/subclass leaves |
| Mapping validation and synchronous handlers in `catch` | `_catch.py`, `test_catch.py` | invalid argument, invalid key/handler, async handler leaves |
| Naked, nested, matched, unmatched and handler-raised behavior | `_catch.py`, `test_catch.py` | catch behavior leaves |
| Group-aware suppression | `_suppress.py`, `test_suppress.py` | naked, partial and full suppression leaves |
| Formatting and printing helpers | `_formatting.py`, `test_formatting.py` | format-only, format, print and print-exc leaves |
| No monkeypatching on modern Python | `__init__.py`, README | modern-runtime identity leaf |

The reverse mapping is exact: every verifier leaf belongs to one row above,
and each row is described in `instruction.md`. Candidate imports occur only in
UID 10001 child processes. The trusted entrypoint exchanges bounded JSON and
does not add `/tmp/candidate-site` to its own `sys.path`.
