# multidict contract traceability

The hidden verifier invokes the candidate only through an unprivileged child-side JSON adapter. The trusted verifier compares 31 deterministic leaf scenarios and owns collection, grading, reward, and network evidence.

| Contract area | Scenarios |
| --- | --- |
| Exports, version, distribution metadata, `py.typed` | `surface-metadata` |
| ABC inheritance and generic aliases | `abc-generics` |
| Pair construction, duplicate order, mapping input | `constructor-duplicates`, `mapping-constructor` |
| First/all lookup, defaults, missing-key errors | `get-contract`, `get-errors` |
| String-only key and containment behavior | `contains-nonstring`, `constructor-errors` |
| Add, assignment, delete, clear, defaults | `add-setitem`, `delete-clear`, `setdefault` |
| Extend/update/merge distinctions | `extend`, `update`, `merge` |
| Pop and error contracts | `popone`, `popall`, `popitem` |
| Case-insensitive mapping and `istr` | `case-insensitive`, `case-update-key`, `istr-contract` |
| Copy and read-only live proxies | `copy-contract`, `proxy-live`, `proxy-readonly`, `proxy-validation`, `ci-proxy` |
| Views, set operations, mutation guard | `views`, `view-sets`, `view-mutation-guard` |
| Equality, versioning, recursive repr | `equality`, `version`, `repr-recursion` |

Every scenario maps to behavior documented in `instruction.md`; no scenario checks private storage names, C symbols, source text, or development-machine paths. Native accelerator, benchmark, pickle-fixture, leak, and static type-checker tests are excluded because the subprocess JSON boundary intentionally covers stable public behavior instead.
