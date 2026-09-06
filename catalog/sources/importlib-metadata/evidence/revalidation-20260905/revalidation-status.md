# importlib-metadata instruction revalidation status

The instruction-migration queue expected source digest
`sha256:999d2d9c026a42bef4dafc682413baf7b3c055890aeb67c7ec70c691b09699d5`.
`nl2repo task validate-source` returned that exact digest before this evidence
was added.

All three declared private artifacts exist in the parent CAS and match their
declared sizes and SHA-256 digests. The current Oracle bundle is nevertheless
not runnable for this campaign: it contains no source payload and its
`solve.sh` fetches the pinned revision from GitHub. No Oracle host, DNS,
registry, or other external-service authorization is allowed.

A bounded trusted-local search recovered the exact full commit from a local uv
Git object cache. A locally generated `git archive` is 225,280 bytes and has
SHA-256
`921c3509959fd9a207da52966da0d4fb2da167e51a9b7a4abb8eff4f46abbf39`,
matching the frozen source declaration. A deterministic replacement Oracle
bundle was built and locally smoke-tested without network. Its proposed digest
and complete inner inventory are in `oracle-replacement-proposal.json`.

The worker did not change `task.toml`, lifecycle state, controls, instruction,
or `production-evidence.json`. It also did not compile or run Harbor against
the unresolved old binding. The parent must register the replacement, update
the binding, compile twice, and run a fresh Oracle/control matrix before the
task can regain current receipts.
