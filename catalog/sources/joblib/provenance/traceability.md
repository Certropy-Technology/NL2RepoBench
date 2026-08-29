# joblib test traceability

The private 33-leaf contract is bidirectionally mapped to the public
instruction:

| Scenario family | Instruction section | Covered behavior |
| --- | --- | --- |
| `exports`, backend/config, delayed, generator, errors | Parallel execution | public exports, ordering, contexts, invalid inputs, exception propagation |
| dump/load, compression, file objects | Persistence | path/file-object round trips and compression semantics |
| NumPy round trip, mmap, compressed mmap | Persistence | array shape/dtype/sum, memmap and warning boundary |
| dictionary/set/NumPy hash and invalid method | Hashing | deterministic canonical hashing and error contract |
| cache, equivalent kwargs, ignore, clear, failed call | Disk cache | cache hits, normalized calls, invalidation and recomputation |
| memstr, wrapper, compressor registration, testing helper | Utilities and extension points | utility conversion and validation behavior |

Every public promise in the selected sections is exercised by at least one
scenario. The upstream suite remains inventory evidence; its Dask and
platform-dependent branches are excluded from the fixed denominator rather
than silently assigned a result.
