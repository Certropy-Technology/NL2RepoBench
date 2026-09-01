# 10: Enable Rust Production Lane

**What to build:** Rust becomes a continuously managed authoring lane using the shared scheduler, candidate funnel, reviews, archives, integration gates, resource guards, and recovery procedures.

**Blocked by:** 09: Publish The First Rust Harbor Task.

**Status:** ready-for-agent

- [ ] Discovery accepts only immutable revisions, distributable licenses, reproducible Cargo closures, and deduplicated candidate identities.
- [ ] The lane uses the shared lease scheduler, one task writer, bounded controllers, fairness, and repository/Docker capacity guards.
- [ ] Every task persists source validation, closure, compile, Oracle, controls, review, archive, and publication evidence.
- [ ] Failure classes remain distinct and only infrastructure failures receive automatic retry.
- [ ] Pause, recovery, cleanup, and status workflows are observable and safe across service restarts.
- [ ] A Rust lane pilot passes without changing generic evaluator semantics or the contracts of other languages.
