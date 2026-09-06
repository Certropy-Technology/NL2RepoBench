# Instruction revalidation blocker

The queue source digest was validated as
`sha256:56d1799c08cb1ca124714b85dc6855ad986c9f4b64519f588d8b25a383a3eebc`.
The current generated projection contains an exact, digest-matching frozen source archive
and a copy of the declared dependency lock, but the private verifier bundle
`sha256:19f82da6b23019bbf1274d54f5d39a17328218dc887a6efa48dcf023725a0ccf` (20,480 bytes)
and Oracle bundle
`sha256:1e7b650df7c1cef0fe360af11da245100c80f886b3f3187aade5434db22c67e7` (880,640 bytes)
are absent from the current private CAS.

Bounded recovery checked the current generated task, tracked task history, historical
authoring handoff locations, and task-named local archive/module caches. No exact-byte
verifier or Oracle payload was found. The lock is recoverable from the projection at
`catalog/tasks/opentelemetry-semantic-conventions/environment/candidate-requirements.lock.txt`,
but this does not establish the missing private bundles.

No network access, runtime Oracle fetch, compile, or Harbor matrix was attempted after the
CAS gate. `task.toml`, lifecycle status, generated runtime, and historical
`production-evidence.json` were left unchanged. The prior receipts are not accepted for
the post-instruction revalidation because they are not bound to durable current receipts.

## Remediation

Recover or reconstruct the exact verifier and Oracle bundle bytes from a trusted local
artifact source, verify each declared size and SHA-256, register them in the parent-owned
private CAS, then compile twice with the locked toolchain and rerun Oracle, empty, stub,
forgery, and supported NoNetwork controls. Do not change the frozen denominator or replace
production evidence until the complete matrix is durable and bound to the resulting
canonical manifest.

Detailed search results are recorded in
`evidence/revalidation-20260905/local-recovery-search.json`.
