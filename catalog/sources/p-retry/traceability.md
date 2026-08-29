# `p-retry` Traceability

The frozen upstream suite collects 70 AVA leaves and one tsd source file. The
private verifier freezes 46 deterministic `node:test` leaves. Timing-heavy
upstream assertions are represented with controlled timers and fixed random
sequences; no hidden assertion depends on an undocumented implementation
helper.

| Public contract | Private coverage |
| --- | --- |
| ESM package identity, version, engine, declarations, exports, exact dependency, and script policy | Package inventory leaf |
| Synchronous and asynchronous results, one-based attempts, finite/default/zero/infinite retry budgets, and final errors | Eight execution and budget leaves |
| Retry, callback, numeric, and removed-option validation | Four validation leaves |
| Non-Error normalization and ordinary versus network-shaped `TypeError` classification | Three error leaves |
| `AbortError` string/Error construction, original error, callback bypass, and immediate stop | Three abort leaves |
| Frozen `RetryContext` fields, callback order, async callbacks, policy decisions, skipped consumption, and callback errors | Ten callback leaves |
| Exponential factor, `maxTimeout`, randomization, non-positive factor normalization, effective `retryDelay`, skipped backoff, and zero `maxRetryTime` | Seven backoff/time leaves |
| Pre-aborted signals, default abort reason, abort during delay, and `unref` timer handling | Four signal/timer leaves |
| `makeRetriable` retry options, argument forwarding, and dynamic `this` | Two wrapper leaves |
| Falsy result preservation, undefined callback defaults, and positive infinity for maximum timeout values | Four boundary leaves |

The adapter accepts only six named operations with bounded JSON payloads.
Candidate code runs as UID 10001 in a resource-limited subprocess; the trusted
test process never imports the package. Callback functions, timer tokens, abort
controllers, and errors are constructed only inside the child. The verifier
owns collection, grading, network proof, and reward files.

The verifier intentionally excludes lint configuration, exact source layout,
exact stack frames, multi-second elapsed-time thresholds, commented upstream
examples, and compile-time inference beyond the documented declarations. These
are explicit task boundaries rather than claims of full upstream parity.
