# 08: Gate The Rust Candidate Funnel

**What to build:** The fixed Rust candidate set is evaluated with the same reproducible source, license, Cargo closure, baseline, specification, verifier, Oracle, and controls gates, promoting only the first complete pass.

**Blocked by:** 07: Complete Rust Synthetic Proof.

**Status:** ready-for-agent

- [ ] `async-channel`, `lexopt`, and `humantime` are checked at their frozen revisions with verified source archives and permissive licenses.
- [ ] Each candidate generates and validates its lock, registry snapshot, vendor store, inventory, and offline closure before locked tests run.
- [ ] Three fresh baselines use the same target list, feature arguments, toolchain, denominator, and failure-set checks.
- [ ] Every funnel receipt binds command, environment, toolchain, image, closure, network, cgroup, output, and log digests.
- [ ] `semver` remains rejected for candidate-owned root build-time code.
- [ ] A first complete pass is promoted; an all-fail result records `no-promotable-candidate` without silently expanding scope.
