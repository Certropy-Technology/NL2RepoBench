# dotenv blocked remediation record

Status: **blocked**. The exact source revision and archive digest are recorded,
but the committed npm lock is v2 while the production Node lane requires the
v3 lock/cache contract. Generated `dist/` provenance, a separate verifier,
frozen denominator, Oracle, and controls are also absent. No runtime task is
generated.

The discovery audit remains at [`evidence/audit.md`](evidence/audit.md). The
pre-descriptor validation probe is preserved at
`evidence/pre-descriptor-validation.txt`.

Reopen only after producing and reviewing an npm lockfile v3 and complete
offline integrity closure, freezing generated `dist/` provenance, narrowing
the JSON-safe parse/populate contract, and running the separate verifier,
Oracle, and controls.
