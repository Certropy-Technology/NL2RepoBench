# Test Traceability

The private verifier contains 24 deterministic `node:test` leaves. Each leaf
maps to a behavior stated in `instruction.md`; names are intentionally kept in
the private bundle so the public task describes behavior without exposing the
rubric implementation.

| Public contract area | Private leaves | Evidence |
| --- | ---: | --- |
| Root ESM package shape and Promise compatibility | 2 | `packaging` cases |
| Executor state, one-shot settlement, and retained reason | 6 | `executor-state` cases |
| `DeferredPromise` constructor and controls | 6 | `deferred-promise` cases |
| Value, native Promise, DeferredPromise, and thenable assimilation | 5 | `thenable-assimilation` cases |
| `catch`, `finally`, and callback error propagation | 5 | `error-and-finally` cases |

The upstream 42-case Vitest suite was inventoried in the task-local source
clone. The production verifier preserves its observable assertions while using
a JSON adapter so trusted tests never import candidate code in the verifier
process. The adapter only transports JSON values and explicit error summaries;
it does not expose private tests or the Oracle source to the candidate.
