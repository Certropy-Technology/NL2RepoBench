# `universalify` Traceability

The frozen denominator is 24 `node:test` leaves. Hidden assertions are grouped
below by public contract section; no test requires an undocumented private
helper or development dependency.

| Public contract | Frozen leaves | Upstream basis |
| --- | ---: | --- |
| CommonJS root has exactly two callable exports | 1 | package entry and `index.js` exports |
| Returned wrappers preserve source `.name` | 2 | both upstream name tests |
| `fromCallback` callback mode, receiver, arguments, and undefined return | 1 | callback-mode upstream case |
| `fromCallback` Promise mode, receiver, arguments, and input-array immutability | 2 | Promise and `.apply` upstream cases |
| `fromCallback` error identity, nullish success, falsey rejection, first result | 6 | upstream error/falsey tests plus README callback contract boundaries |
| `fromCallback` final-position detection and sync/throw semantics | 3 | implementation-level public wrapper semantics required by README API |
| `fromPromise` callback mode, receiver, arguments, callback removal | 2 | callback and optional-argument upstream cases |
| `fromPromise` unchanged Promise result and Promise-mode receiver | 2 | Promise-mode upstream case and source-return contract |
| `fromPromise` rejection forwarding, falsey reason, callback throw once | 4 | upstream error and unhandled-rejection cases plus falsey boundary |
| Valid thenable support | 1 | README requirement that the source return a valid JS Promise-compatible value |

The instruction also forbids runtime dependencies, lifecycle scripts, custom
loaders, native addons, and network behavior. Those constraints are enforced
by the npm package validator, offline installation, static network policy, and
negative controls rather than by adding functional leaves to the denominator.
