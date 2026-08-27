# `p-limit` Traceability

The frozen upstream suite has 22 AVA leaves. The private verifier freezes 24
deterministic `node:test` leaves because several upstream tests combine
multiple independently specified behaviors. No hidden assertion relies on an
undocumented implementation helper.

| Public contract | Private coverage |
| --- | --- |
| ESM package identity, version, declarations, exports, dependency and script policy | Package inventory leaf |
| Numeric/options constructors, positive infinity, invalid inputs | Four constructor leaves |
| Concurrency bound and serial execution | Numeric/options and concurrency wave leaves |
| Argument forwarding, synchronous values, throws, rejections and queue continuation | Five execution leaves |
| Asynchronous start and AsyncLocalStorage preservation | Async-start and async-context leaves |
| Active/pending counters | Initial/final count leaf and clear leaves |
| `clearQueue`, active-task preservation and `rejectOnClear` | Two clear leaves |
| `map` order, index, array/Set/iterator inputs and detached use | Four map leaves |
| Dynamic concurrency increase/decrease | Two setter leaves |
| `limitFunction` argument forwarding and independent bound | One `limitFunction` leaf |

The adapter accepts only named scenarios and bounded JSON data. Candidate code
runs as UID 10001 in a separate process; the trusted test process never imports
the package. The verifier owns collection, grading, network proof, and reward
files.
