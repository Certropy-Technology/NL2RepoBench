# Nock revalidation blocker (2026-09-05)

The queue entry requires revalidation because the instruction changed and prior
receipts are not current. The queue source digest is
`sha256:43c6427c5a6414bb351f780f9cb7716948722c9f36aa51fa319e7055aa96de61`;
`uv run nl2repo task validate-source catalog/sources/nock` passed before any
source mutation.

All four declared private artifacts were found in the parent CAS and passed
offline exact-size and SHA-256 checks. Two independent production compiles
also passed and produced byte-identical bundles, recorded in
`compile-summary.json`. The generated bundle was not installed as the current
projection because no fresh valid Oracle receipt exists.

The checked-in Oracle bundle's `solve.sh` performs `git fetch` from
`https://github.com/nock/nock` at runtime. This is forbidden under the task's
`no-network` policy. A bounded search of the checked-in projection, CAS,
retained local archives, and historical authoring records found only a stale
historical path reference; the exact source archive with digest
`sha256:8c54a05e667935a42b69be72e1a95d0fb027805068dcc11b0d42b654525e0918`
was not available. Oracle execution and all controls were therefore not run.

Lifecycle, `task.toml`, generated projection, and existing production evidence
remain unchanged. Remediation: register the exact frozen source archive in
the parent CAS (or provide an equivalent provenance-proof local Oracle
payload), recompile twice, then run a fresh NoNetwork Oracle/control matrix
and bind all durable receipts before promotion.
