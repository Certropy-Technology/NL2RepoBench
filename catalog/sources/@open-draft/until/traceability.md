# `until-async` Traceability

The frozen upstream suite contains two runtime and two declaration tests. The
private verifier freezes 18 deterministic `node:test` leaves because each
public outcome and package constraint must remain independently scoreable. No
hidden assertion relies on an undocumented helper or source layout.

| Public contract | Private coverage |
| --- | --- |
| npm name/version, ESM root, package-json export, no default export | Package inventory leaf |
| Zero runtime/dev dependencies and scripts | Package inventory leaf plus offline installer |
| `UntilResult` generic two-tuple union and `until` signature | Declaration leaf |
| Fulfillment returns `[null, data]` without falsey-value coercion | Six fulfillment leaves |
| Promise rejection returns `[reason, null]` and preserves Error/value reasons | Four rejection leaves |
| Synchronous callback throws are captured | Two throw leaves |
| Callback is invoked exactly once | Callback-count leaf |
| Settlement works after asynchronous turns | Delayed success and rejection leaves |
| Independent concurrent calls preserve their own values | Parallel-call leaf |

The trusted process only runs `node:test` and starts a UID 10001 child through
`runuser`, `timeout`, and `prlimit`. The child owns callback construction and
candidate import. Collection, network proof, grading, and reward remain
verifier-owned.
