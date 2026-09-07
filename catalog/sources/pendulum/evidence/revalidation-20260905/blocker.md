# Pendulum instruction-migration revalidation blocker

## Classification

- task: `pendulum`
- source revision: `0d71391ab2b617b2e86d15c926e6cde9fddc5676`
- required source archive: `sha256:bcc6303eabd924e272cde41cf251ef7c0a383594a67633bfd2005f8c2f777404`
- classification: `artifact-or-verifier-blocked`
- status: no fresh Oracle or control result claimed

The instruction bytes changed after the prior production receipts. Those receipts
are not current and were not reused. The trusted local CAS contains exact matches
for the declared dependency lock, verifier bundle, and Oracle bundle; exact sizes,
hashes, and the Oracle inventory are recorded in `artifact-integrity.json`.

The Oracle bundle has no frozen source archive. Its `solve.sh` instead performs a
runtime clone/fetch from the upstream Git host before checking the declared source
archive digest. That violates this revalidation's NoNetwork contract, so it was not
executed and no source-host authorization was added. A bounded search of trusted
local CAS, historical handoffs, worktree archives, and source/tarball candidates
found no file matching the required source digest.

## Commands and results

The following commands were run from the isolated task worktree; paths are shown
as normalized placeholders to keep evidence portable:

| Stage | Command | Result |
| --- | --- | --- |
| Queue/source preflight | `python3 -c 'read queue entry and compare source digest'` | exit 0; queue digest equals `sha256:4188a222e8847…81a42` |
| Source validation | `uv run nl2repo task validate-source catalog/sources/pendulum` | exit 0 |
| CLI/toolchain | `uv run nl2repo --help`; `uv run --frozen --project harbor-runner harbor --version` | exit 0; Harbor `0.21.0` |
| Dependency artifact check | `stat` and `sha256sum` for the declared lock CAS object | exit 0; 7,381 bytes and exact digest |
| Verifier artifact check | `stat` and `sha256sum` for the declared verifier CAS object | exit 0; 20,480 bytes and exact digest |
| Oracle artifact check | `stat` and `sha256sum` for the declared Oracle CAS object | exit 0; 491,520 bytes and exact digest |
| Oracle inventory | `tar -tf <oracle-bundle>` | exit 0; only `solve.sh`, `pyproject.toml`, and the frozen extension; no source archive |
| Source recovery | bounded hash scan over trusted local archives, handoffs, caches, and historical worktrees | exit 0; no exact archive match |
| Oracle/control matrix | Harbor 0.21.0 Oracle and controls | not run; unsafe runtime source fetch and missing exact offline source |

All runtime execution remained network-isolated. No GitHub, codeload, package
registry, DNS, or external service was authorized or contacted.

## Skipped sets and remediation

Skipped gates: fresh compile, Oracle, empty, stub, forgery, install-hang, call-hang,
and offline controls. The prior 47-leaf denominator is retained only as historical
context; it is not a current receipt for the migrated instruction.

Next unblock action: provide an independently provenance-bound archive whose bytes
hash to `sha256:bcc6303eabd924e272cde41cf251ef7c0a383594a67633bfd2005f8c2f777404`,
or register a parent-reviewed replacement Oracle bundle that embeds the exact
revision without network fetch. The parent must then compile twice with the locked
toolchain and run a complete fresh NoNetwork matrix before updating any projection
or production evidence.
