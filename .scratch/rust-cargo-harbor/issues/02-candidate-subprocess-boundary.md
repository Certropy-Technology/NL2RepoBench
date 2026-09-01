# 02: Deliver Candidate Subprocess Boundary

**What to build:** Candidate, bridge, and CLI executions run through one bounded process contract that prevents host escape, cleans up descendants, and returns stable structured outcomes.

**Blocked by:** None (F0 canonical foundation is integrated).

**Status:** ready-for-agent

- [ ] UID/GID, no-new-privileges, zero capabilities, exact argv, safe cwd, and executable roots are enforced.
- [ ] Wall, CPU, memory, swap, process, file, descriptor, input, and output limits are enforced and recorded.
- [ ] Process groups, sessions, double-fork descendants, UID residue, timeout, OOM, and cleanup behavior have fault tests.
- [ ] Spawn, timeout, output-limit, cleanup, and abnormal-exit results use one stable schema and error precedence.
- [ ] Direct subprocess bypasses and the removed address-space-limit path are rejected by the boundary gate.
- [ ] Shared evaluator and existing language scoring behavior remain unchanged.
