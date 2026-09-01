# 03: Freeze Rust Cargo Foundation

**What to build:** A Rust authoring source can be validated as the canonical `rust+cargo` runtime and can produce a reproducible, offline, task-scoped Cargo dependency closure for the fixed Linux target.

**Blocked by:** 01: Implement Private CAS Staging; 02: Deliver Candidate Subprocess Boundary.

**Status:** ready-for-agent

- [ ] Only the `rust+cargo` runtime pair is accepted by canonical validation and registry dispatch.
- [ ] The source profile fixes `x86_64-unknown-linux-gnu`, one release-wide toolchain profile, exact features, target selectors, and candidate dependency permissions.
- [ ] Closure preparation, vendorization, and offline consumption use separate trusted command profiles.
- [ ] Cargo.lock, registry snapshot, crate archives, vendor tree, inventory, and toolchain outputs are hash-bound.
- [ ] Candidate-owned build scripts, procedural macros, workspaces, mutable sources, native linking, and custom toolchain overrides fail closed.
- [ ] A fresh network-disabled consumption run succeeds without relying on the host Cargo cache.
