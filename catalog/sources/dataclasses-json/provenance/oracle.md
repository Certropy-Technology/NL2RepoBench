# Oracle And Remediation Evidence

The frozen Git archive for `dc63902eeb5e1c5ce1ea4e078c50e0eb9bc1a541` was
re-fetched and verified as
`sha256:113c90da5957f13cc49f80d535cde965e66850f72559498a9ebfd934c4db449f`.
The rebuilt private Oracle bundle asserts both the fetched revision and this
archive checksum before it materializes `/workspace`.

The production compiler was run with the task-local `.nl2repo/artifacts`
store and `--allow-private`. The generated verifier and candidate images both
build from the digest-pinned Python 3.12 image. The direct separate-verifier
probe mounted the verified archive as a writable Harbor-equivalent workspace
and used `--network none`:

- `valid=true`
- `collected=24`, `expected=24`, `passed=24`
- `reward=1.0`
- verifier network probes for `1.1.1.1:443` and `pypi.org:443` were both false
- evidence: `.nl2repo/evidence/oracle-direct/logs/grading.json`,
  `collection.json`, `candidate-install.json`, and `network.json`

The frozen source needs `POETRY_DYNAMIC_VERSIONING_BYPASS=0.0.0` while it is
built from an archive without `.git`. A minimal generic compiler/verifier fix
now passes the already-validated custom verifier environment into the isolated
candidate build process; it does not expose it to agent runtime. No Harbor
Agent Run was started by this lane.

The public catalog contains no verifier/test bytes. The custom adapter and
dependency/Oracle bundles are addressed by private refs in `task.toml`; the
generic compiler materializes them only in the separate verifier image.
