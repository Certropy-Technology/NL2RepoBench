# `p-map` Traceability

The frozen upstream revision exposes three runtime exports and contains timing-
dependent AVA tests. The private verifier freezes 30 deterministic `node:test`
leaves around the documented behavior.

| Public contract | Private coverage |
| --- | --- |
| ESM package identity, version, root export map, declarations, and no runtime dependencies | Package inventory leaf |
| `pMap` sync values, promise-valued inputs, async iterables, mapper arguments, and output order | Six value/order leaves |
| Concurrency bound, asynchronous invocation, and positive infinity | Three scheduling leaves |
| Iterable, mapper, concurrency, and backpressure validation | Validation leaves |
| `stopOnError`, aggregate errors, source errors, and abort signals | Error/abort leaves |
| `pMapSkip` for arrays and async iterable results | Skip leaves |
| `pMapIterable` order, index, mapper errors, source errors, and backpressure | Eight async-iterable leaves |

The adapter accepts only bounded operation names and JSON-compatible scenario
parameters. Controlled promises, async generators, errors, and the skip symbol
are constructed inside the UID-separated candidate child. The trusted test
process never imports candidate code and owns all grading/report files.
