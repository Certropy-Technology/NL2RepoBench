# 01: Implement Private CAS Staging

**What to build:** Existing benchmark tasks can be compiled from public artifact references while private dependencies, tests, verifier code, and Oracle material are available only to their authorized execution role.

**Blocked by:** None (F0 canonical foundation is integrated).

**Status:** ready-for-agent

- [ ] Public task projections contain no private lock, vendor, hidden test, verifier, Oracle, CAS, or host-path bytes.
- [ ] Task-scoped authorization validates every reference, media type, inventory, digest, role, and visibility before materialization.
- [ ] Candidate and model namespaces cannot read private material; the separate verifier can read only its authorized roots.
- [ ] Provider capability failure never falls back to private `COPY`, public URLs, or network access.
- [ ] Successful staging, quarantine, cleanup, and cleanup failure all produce bounded verifiable receipts.
- [ ] At least one Python, Node, and Go task pass deterministic compile and private-visibility controls.
