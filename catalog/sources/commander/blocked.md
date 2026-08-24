# commander blocked remediation record

Status: **blocked before source freeze**.

The candidate URL is `https://github.com/tj/commander.js`. The bounded lane did
not obtain a trusted full commit, reproducible Git archive, or exact license
bytes. The project-level license claim is MIT only; it is not treated as
license-byte evidence. No runtime task, hidden tests, private verifier, Oracle,
or controls were generated.

The exact failed descriptor-validation probe is preserved in
`evidence/descriptor-validation.log`. It exited `1` because the descriptor did
not yet exist. This is authoring/source evidence, not a fabricated build or
Oracle result.

Reopen only after resolving one canonical upstream commit, reproducing archive
and license hashes, then freezing Node/npm versions, the lock/cache closure,
the CJS/ESM boundary, collection, separate verifier, Oracle, and controls.
