# Contract Traceability

The private verifier emits exactly 28 unique `custom-json-v1` leaves. Every
candidate import and behavior probe runs in a UID-isolated child process. The
trusted parent owns collection, JUnit, grading, reward, and network artifacts.

| Contract area | Leaves |
| --- | --- |
| Distribution and exports | `package-identity`, `root-exports` |
| Header data structure | `headers-init`, `headers-lookup`, `headers-duplicates`, `headers-mutation`, `headers-serialize`, `headers-invalid`, `headers-copy` |
| URI parsing | `uri-basic`, `uri-secure-userinfo`, `uri-idna`, `uri-invalid-scheme`, `uri-invalid-fragment` |
| Frame and close codecs | `frame-text`, `frame-masked`, `frame-long`, `frame-parse`, `frame-invalid`, `close-roundtrip`, `close-invalid` |
| Exceptions | `exception-contract` |
| Protocol | `protocol-receive`, `protocol-send`, `protocol-close` |
| Asyncio message assembly | `assembler-fragments`, `assembler-binary-decode`, `assembler-concurrency` |

The full upstream baseline is retained in task-local provenance. The 28-leaf
denominator is intentionally deterministic and does not require a live server.
