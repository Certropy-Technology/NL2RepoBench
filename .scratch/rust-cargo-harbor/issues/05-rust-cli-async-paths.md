# 05: Add Rust CLI And Async Paths

**What to build:** The synthetic Rust task also exercises a command-line binary and executor-neutral asynchronous functions while preserving the generic candidate process boundary.

**Blocked by:** 04: Run Rust Library Tracer Bullet.

**Status:** ready-for-agent

- [ ] CLI behavior is limited to arguments, standard input/output/error, exit status, and a task-scoped temporary directory.
- [ ] Rust-local CLI invocations convert losslessly to the existing generic process request without changing that contract.
- [ ] CLI limits, expected exits, output, temporary-directory policy, and observations are frozen and receipt-bound.
- [ ] Candidate output is physically separated from bridge protocol output and output flooding remains attributable to the candidate.
- [ ] Async functions run through a verifier-owned executor without binding the generic contract to a specific async runtime.
- [ ] Normal, declared-error, timeout, output-limit, and cleanup outcomes map deterministically to leaves.
