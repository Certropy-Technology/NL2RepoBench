# Emittery Traceability

The private contract preserves representative assertions from the frozen
upstream `test/index.js` suite while adapting callbacks, symbols, AbortSignals,
iterators, and class decorators into deterministic child-side scenarios.

| Public specification area | Private scenarios | Upstream behavior families |
| --- | --- | --- |
| package shape and root exports | `metadata`, `method-surface` | package metadata, constructor surface |
| subscriptions and event objects | `on-basic`, `on-multiple`, `on-dedupe`, `event-name-types`, `listener-validation`, `data-shape`, `isolated-events`, `on-abort`, `disposable` | `on()`, `off()`, event names, abort, disposal |
| concurrent and serial emission | `emit-concurrent`, `emit-errors`, `serial-order`, `serial-error` | `emit()`, `emitSerial()`, listener errors |
| any-event subscriptions and counts | `any-listener`, `any-abort`, `listener-count` | `onAny()`, `offAny()`, `listenerCount()` |
| one-shot subscriptions | `once-basic`, `once-multiple`, `once-predicate`, `once-validation`, `once-cancel`, `once-abort` | `once()` predicate, cancellation, signal |
| async iterators | `events-buffer`, `events-multiple`, `events-return`, `events-abort`, `any-event`, `any-event-abort` | `events()`, `anyEvent()`, buffering and cleanup |
| clearing and forwarding | `clear-selected`, `clear-all`, `bind-methods`, `bind-validation`, `mixin`, `mixin-validation` | `clearListeners()`, `bindMethods()`, `mixin()` |
| reserved symbols and lifecycle | `meta-events`, `meta-blocked`, `init-lifecycle`, `init-immediate`, `init-clear`, `init-validation`, `init-rollback` | meta events and `init()` cleanup/rollback |
| debugging | `debug` | debug operation records |

The adapter accepts no executable strings, callbacks, symbols, promises, or
candidate objects. It constructs those values internally and returns only
bounded JSON. The trusted test process never imports candidate code; each leaf
spawns the candidate-side adapter as UID 10001.
