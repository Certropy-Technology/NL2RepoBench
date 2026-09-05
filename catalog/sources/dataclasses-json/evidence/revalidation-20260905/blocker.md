# dataclasses-json instruction revalidation blocker

- Revalidation date: 2026-09-05.
- Current catalog source digest: `sha256:ffdfada24b0013c56bd5480f558758b35aeeba5927cd2cf0e4c5e7041f9ea5c5`.
- `uv run nl2repo task validate-source catalog/sources/dataclasses-json` exited 0.
- `uv run python scripts/validate_instruction_quality.py` exited 0.
- Strict source network lint reported zero errors and no task-specific findings.

The dependency lock, verifier bundle, and Oracle bundle were checked in the
parent private CAS. Each declared digest and size matched. Two production
compiles with the locked Python toolchain and `--allow-private` exited 0 and
were byte-identical. Their canonical manifest digest is
`sha256:420d9df622be8e03c76288a95c4663b08e81424d0e01a0338408cc3fad8c4bbc` and
the bundle manifest SHA-256 is
`sha256:24c28210e9d23294f7a5ecb966589d7a202d8eebd794c2f445bfa50ecfacf6a6`.

Before any runtime execution, the Oracle tar payload was inspected. Its
`solve.sh` runs `git -C "$SOURCE_DIR" fetch --depth 1 origin
"$UPSTREAM_REVISION"` against `https://github.com/lidatong/dataclasses-json.git`.
This violates the required NoNetwork contract, so Oracle, empty, stub, forgery,
and offline controls were blocked before run. No reward or collection result
is claimed. The existing lifecycle and historical `production-evidence.json`
were left unchanged because their old receipts are not durable current
evidence.

Remediation: register a local Oracle payload containing the exact frozen source
archive, verify the revision and archive digest, recompile, and rerun the full
NoNetwork Oracle/control matrix. The structured details and compile evidence
are in `blocker.json` and the adjacent JSON summaries.
