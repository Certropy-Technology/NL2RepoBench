# 07: Complete Rust Synthetic Proof

**What to build:** A complete synthetic Rust Harbor task demonstrates the entire v1 platform contract and proves that private staging, subprocess isolation, Cargo closure, bridge execution, reporting, and controls work together.

**Blocked by:** 06: Add Rust State And Bounded Unsafe Paths.

**Status:** ready-for-agent

- [ ] One fixture covers library, CLI, async, non-empty pure Rust closure, state handles, and bounded serializable unsafe functions.
- [ ] All frozen leaves collect consistently with the declared denominator and use the stable Rust bridge report format.
- [ ] Oracle, empty, stub, forgery, offline, panic, abort/crash, hang, output-flood, child-process, build-time-code, and private-mount controls pass.
- [ ] Compile, generated bridge, public projection, and execution identity are deterministic across repeated runs.
- [ ] Private scans cover source projections, Harbor contexts, images, caches, logs, reports, and exported artifacts.
- [ ] The R0 seam audit proves no Rust business logic was added to the generic evaluator, dependency model, subprocess supervisor, or task writer.
