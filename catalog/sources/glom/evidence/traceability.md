# glom traceability

| Public contract area | Frozen upstream evidence | Private scenario IDs |
| --- | --- | --- |
| dotted and explicit paths, specs, literals | `glom/test/test_basic.py`, `glom/core.py` | `basic-access`, `explicit-path`, `spec-scope`, `val-fill-pipe` |
| calls, invocation, recursive refs | `glom/test/test_basic.py` | `call-and-invoke`, `ref-recursive`, `construction-and-t` |
| fallback and matching | `glom/test/test_basic.py`, `glom/test/test_match.py` | `coalesce-contract`, `match-mapping`, `match-logic`, `check-and-switch`, `match-error`, `path-error` |
| in-place mutation | `glom/test/test_mutation.py` | `assign-existing`, `assign-missing`, `assign-spec`, `delete-contract` |
| lazy iteration | `glom/test/test_streaming.py` | `iter-map-filter`, `iter-chunk-window`, `iter-unique-slice`, `iter-flatten-split`, `iter-terminal` |
| reductions and grouping | `glom/test/test_reduction.py`, `glom/test/test_grouping.py` | `reductions`, `fold-custom`, `grouping` |
| registry and CLI | `glom/test/test_target_types.py`, `glom/test/test_cli.py` | `glommer-registry`, `cli-json` |
| root exports and version | `glom/__init__.py`, `setup.py` | `api-surface` |

The frozen upstream suite was collected at 202 tests and passed 202 tests in
the task-local Python 3.12 probe. The Harbor denominator is the 28 deterministic
JSON cases above, not the upstream test count; this avoids crossing Python
objects and arbitrary callbacks through the verifier boundary.
