# pycparser instruction revalidation blocker

- Current migrated source digest: `sha256:ce5e4d779eb9d885d6d4617a6b949c390147efbba708dc239d96e984cd716adf`.
- Frozen revision: `10d17757e282d8af5426d6df4d55eb394042b550`.
- Frozen source archive: `sha256:ed31469eea243e25ce86310039c174a61890d2acc7586cd06f8be38cf1baf5a1`, 1,331,200 bytes.
- Existing lifecycle and historical `production-evidence.json` remain unchanged.

## Checks and local recovery

The dependency lock, verifier bundle, and Oracle bundle were present and matched
their declared sizes and SHA-256 digests. Two production compiles with the locked
Python toolchain completed with exit code 0 and were byte-identical. The compiled
bundle has 60 files including its manifest; the manifest SHA-256 is
`sha256:345b4e383e431009105069d046479154baba9fc5f2896f748bdb0896841049a8` and
the canonical manifest digest is
`sha256:d10af582920f9baaca55128f4f43e0dad910e7d34cddc8543a7d4ae9ebc34f53`.

Bounded searches of the current source and projection, task-local assets, private
artifact store, cached archives, retained handoffs, and historical generated
worktrees found no file whose bytes matched the frozen 1,331,200-byte archive
digest. No replacement payload was constructed or proposed.

## NoNetwork blocker

The exact Oracle bundle contains only `solve.sh`. Its source acquisition step runs
`git fetch` from `github.com` at the frozen revision and only then creates and
checks the archive digest. It does not contain `source.tar` or another local
source payload. This violates the required NoNetwork contract, so no Harbor
Oracle or control run was started. No reward, collection, or fresh production
receipt is claimed. The historical receipt is not rebound to the migrated source.

The complete structured command, artifact, compile, and remediation evidence is
in `blocker.json`; command summaries and artifact hashes are in `command-log.txt`.

## Remediation

Register a trusted private Oracle payload containing the exact frozen source
archive, or an equivalent local revision- and digest-verified materialization.
Then compile twice, inspect the final bundle, and run Oracle plus empty, stub,
forgery, offline, install-hang, and call-hang controls with network isolation.
