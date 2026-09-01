# 06: Add Rust State And Bounded Unsafe Paths

**What to build:** The synthetic task supports bounded opaque state and serializable unsafe functions while isolating state lifetime, crashes, and unsafe assertions from the rest of the run.

**Blocked by:** 05: Add Rust CLI And Async Paths.

**Status:** ready-for-agent

- [ ] State creation, calls, and drops use bounded process-local handles that cannot cross leaves or processes.
- [ ] Handle count, serialized state, operation batch, timeout, and ownership limits are enforced.
- [ ] Unsafe functions accept and return only serializable values; raw pointers, references across the bridge, FFI, linking, assembly, and allocators are rejected.
- [ ] Every unsafe leaf runs in a fresh candidate process and panic, abort, timeout, or OOM cannot contaminate later leaves.
- [ ] Miri uses the locked offline sysroot and vendor closure; unsupported or failing Miri blocks Oracle validity.
- [ ] The benchmark makes no memory-safety claim and keeps Miri outside the reward metric.
