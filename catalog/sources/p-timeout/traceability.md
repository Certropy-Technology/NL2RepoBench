# `p-timeout` Traceability

The frozen upstream suite has 20 AVA leaves plus tsd declarations. The private
verifier freezes 35 deterministic `node:test` leaves because upstream leaves
combine multiple independently documented paths. No hidden assertion depends
on a private implementation helper.

| Public contract | Private coverage |
| --- | --- |
| ESM package identity, version, entries, files, scripts, and zero dependencies | Package contract leaf |
| Default `pTimeout` and named `TimeoutError` exports | Export leaf |
| `TimeoutError` inheritance, name, message, and cause | Error class leaf |
| Positive, fractional, and infinite milliseconds; invalid domains | Ten validation leaves |
| Promise and PromiseLike fulfillment/rejection adoption | Three input leaves |
| Default, string, empty, Error, and false timeout messages | Five timeout leaves |
| Cancelable input behavior and timeout precedence | Timeout and cancellation leaves |
| Sync/async fallback values, throws, and rejections | Four fallback leaves |
| Clearable Promise shape and idempotent `clear()` | Resolve and clear leaves |
| Custom timer argument, receiver, handle, and cleanup behavior | Resolve, timeout, clear, and Infinity leaves |
| Already-aborted signal, custom reason, and Infinity | Three pre-abort leaves |
| One-shot abort listener and cleanup after all terminal paths | Four listener leaves |

The verifier-owned test process reads only package metadata and starts a
resource-bounded UID 10001 child for runtime behavior. That child receives a
named scenario and bounded JSON parameters, constructs callbacks and native
objects locally, imports only `p-timeout`, and returns bounded JSON. The trusted
process owns collection, grading, network proof, and reward files.
