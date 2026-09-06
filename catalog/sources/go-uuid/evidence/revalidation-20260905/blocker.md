# Revalidation Blocker

- Task: `go-uuid`
- Queue source digest (validated before changes): `sha256:d63e3e18ac5a63c7c0e003796e8d49e99d9c72745be2785fefb4c303f331ecf1`
- Frozen upstream revision: `2d3c2a9cc518326daf99a383f07c4d3c44317e4d`
- Frozen source archive digest required by the Oracle: `sha256:e08c0dc34cb6ca21d5ebff08053403b8bf4e91efb97aa2eccf25f17d879bb217`
- Frozen source archive size: not declared in `task.toml` or the existing source-freeze evidence.
- Lifecycle and `production-evidence.json` were preserved unchanged.

## Declared artifact checks

The declared private artifacts exist locally and therefore did not cause an
artifact-missing short circuit:

| artifact | digest | size | result |
| --- | --- | ---: | --- |
| Oracle bundle | `sha256:a3900cb4f9517d3d126230edf28d8a8dc27be2acfb782aaa242a4fc1560951fc` | 739 bytes | present and hash-correct |
| Go module bundle | `sha256:13eef327dbfbe50b6bf6c3e111a9d16e77385846458fbbc5997025a153994e3d` | 476 bytes | present and hash-correct |

The Oracle bundle inventory contains only `solve.sh`; its script fetches the
revision from `https://github.com/google/uuid` at runtime and verifies the
archive against the frozen source digest. No source payload is bundled.

## Bounded local recovery

All searches were offline and used only local files:

| command/result | exit |
| --- | ---: |
| `uv run nl2repo task validate-source catalog/sources/go-uuid` -> queue digest `sha256:d63e3e18ac5a63c7c0e003796e8d49e99d9c72745be2785fefb4c303f331ecf1` | 0 |
| `sha256sum` and `stat` for both declared CAS objects -> exact digest and declared size for each | 0 |
| `tar -tf <Oracle CAS object>` -> `solve.sh` only; no `source.tar` or installable source payload | 0 |
| `find .nl2repo/supervisor/compile/go-uuid -name source.tar` -> zero files | 0 |
| exact digest lookup at `.nl2repo/artifacts/private/sha256/e0/e08c0dc34cb6ca21d5ebff08053403b8bf4e91efb97aa2eccf25f17d879bb217` -> missing | 1 |
| exact digest lookup at `.nl2repo/artifacts/private/sha256/d6/d63e3e18ac5a63c7c0e003796e8d49e99d9c72745be2785fefb4c303f331ecf1` -> missing (catalog digest is not a private payload) | 1 |
| `find` over the known local `go-uuid` worktree/archive-receipt paths for `source.tar` -> zero candidates; task-local evidence, prior compiled runtime, and retained receipts contain no source payload | 0 |

Post-blocker validation also passed without changing the task contract:

| command/result | exit |
| --- | ---: |
| `uv run nl2repo task validate-source catalog/sources/go-uuid` -> queue source digest unchanged | 0 |
| `uv run python scripts/validate_instruction_quality.py` -> instruction quality passed | 0 |
| `gofmt -d harbor/tests/bridge.go` and `bash -n harbor/controls/*.sh` -> no diagnostics | 0 |
| JSON/TOML parser check over the task source and evidence -> passed | 0 |
| `uv run nl2repo task lint-network --tasks-root catalog/sources --include-generated` -> `go-uuid` has 0 errors and 1 Oracle warning; command exit 1 is from 1 unrelated global generated-root error | 1 |
| path/leak scan and `git diff --check` -> passed | 0 |

Historical task evidence confirms that the prior Oracle obtained the source by
network fetch. Its successful receipt is not a reusable local source payload
for this NoNetwork revalidation.

## Result and next step

No exact source archive bytes tied to the frozen revision and required digest
could be proven locally. The Oracle cannot be run under the mandatory NoNetwork
policy without weakening the task contract. No compile, Harbor run, control,
projection, lifecycle, or production-evidence change was made.

Next step: the parent should register a privately authorized local payload only
after independently verifying the full archive bytes, revision, inventory, and
`sha256:e08c0dc34cb6ca21d5ebff08053403b8bf4e91efb97aa2eccf25f17d879bb217`.
