# frozenlist contract traceability

The hidden verifier uses 21 child-side JSON scenarios. Candidate code runs only
as UID 10001 and returns JSON-safe observations; the trusted process performs
all comparisons and owns grading output.

| Public contract | Verifier scenarios |
| --- | --- |
| Distribution identity, version, exports, `py.typed`, stub | `exports-version-metadata` |
| `MutableSequence` and generic aliases | `generic-mutable-sequence` |
| Constructor consumes iterable without aliasing | `constructor-copy-iteration` |
| Index, slice, slice assignment/deletion, reverse iteration | `index-slice-reversed` |
| Equality and total ordering | `comparisons` |
| `insert`, `append`, `extend`, `+=` | `insert-append-extend-iadd` |
| `remove`, `clear`, `reverse`, `pop` | `remove-clear-reverse-pop` |
| `count`, `index`, containment | `count-index-contains` |
| Frozen state, idempotence, exact representation | `freeze-idempotent-repr` |
| Frozen item assignment | `frozen-setitem` |
| Frozen deletion and slice deletion | `frozen-delitem` |
| Frozen insertion | `frozen-insert` |
| Frozen append/extend/in-place addition | `frozen-append-extend-iadd` |
| Frozen remove/clear/reverse/pop | `frozen-remove-clear-reverse-pop` |
| Unfrozen hash rejection and frozen tuple hash | `hash-contract` |
| Shallow copy storage and frozen-state behavior | `shallow-copy` |
| Deep copy nested state | `deepcopy-nested` |
| Deep copy self-cycle | `deepcopy-circular` |
| Deep copy shared aliases | `deepcopy-shared-reference` |
| `PyFrozenList` parity | `pyfrozenlist-parity` |
| `FROZENLIST_NO_EXTENSIONS=1` import selection | `pure-python-selection` |

Reverse traceability is one-to-one at the leaf level: every scenario above maps
to at least one documented public behavior, and no scenario inspects private
storage names, C symbols, generated filenames, upstream source text, or network
behavior.

The two upstream tests excluded from the task denominator assert a historical
`NO_EXTENSIONS` module constant that this exact revision does not expose after
re-import. The environment variable's observable implementation-selection
behavior remains covered by `pure-python-selection`.
