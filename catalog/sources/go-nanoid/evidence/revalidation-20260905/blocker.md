# Instruction Revalidation Blocker

## Binding

- task: `go-nanoid`
- expected queue source digest: `sha256:fd5b3d8918ec49071902cbb973e79e2ceced8a098bc21a662ccbc2ac60c1f0a6`
- frozen upstream revision: `2ab893bb7af49f55a4180d22371fbe9f954203b4`
- required source archive: `sha256:18957a3e43ffb9b662c49467f7b52beadd78292bfb81505ba85d01bc2411a4b7`, 30720 bytes
- current lifecycle: `packaged` (preserved)

## Verified CAS

All declared private CAS objects were present and byte-exact before this blocker was recorded:

| object | digest | bytes |
| --- | --- | ---: |
| Oracle bundle | `sha256:d38211520d6bac15383e35680fb184873140c2a37ab3b803f258dffa4da7a2e6` | 572 |
| Go module bundle | `sha256:9d73397f11b7aea254c710dc316bf32d16cf6d08c5b99ef43b87c581ca34811d` | 491 |
| verifier bundle | `sha256:5ed6a32b885a87beffbfaa8ca0a8b547ab756e180df39957a098c72ace02a538` | 1242 |

The Oracle tar contains only `solve.sh`; it does not contain `source.tar`, an
`oracle-package/`, or another local source payload. Its script clones the
upstream repository and therefore cannot run under the mandatory NoNetwork
policy.

## Bounded Local Recovery

The following searches were performed without network access:

1. Inspected the Oracle tar and task-local `evidence/`, `harbor/`, and prior
   production evidence. Result: no source payload.
2. Searched retained `go-nanoid` authoring worktrees and historical handoff
   records under `.nl2repo/authoring-live` and the worker handoff store.
   Result: only declarations, scripts, and evidence; no matching archive.
3. Searched retained source archives with the frozen archive size and checked
   candidate archive hashes where available. Result: no file matched
   `sha256:18957a3e43ffb9b662c49467f7b52beadd78292bfb81505ba85d01bc2411a4b7`.
4. Checked local Go/module cache locations for a `go-nanoid` source payload.
   Result: no usable source archive was present.

The current source validation was successful and confirmed the expected queue
digest. No compile, Harbor Oracle, or control run was attempted because the
trusted Oracle source bytes cannot be proven locally and runtime fetching is
forbidden.

## Verification Results

- `uv run nl2repo task validate-source catalog/sources/go-nanoid`: exit 0;
  source digest `sha256:fd5b3d8918ec49071902cbb973e79e2ceced8a098bc21a662ccbc2ac60c1f0a6`.
- `uv run python scripts/validate_instruction_quality.py`: exit 0;
  instruction quality passed.
- `bash -n catalog/sources/go-nanoid/harbor/controls/*.sh`: exit 0.
- `gofmt -d catalog/sources/go-nanoid/harbor/tests/bridge.go`: exit 0.
- Task-local JSON and TOML parser check: exit 0.
- `uv run nl2repo task lint-network --tasks-root catalog/sources`: target
  `go-nanoid` findings had zero errors; Oracle source-host authorization is
  intentionally not added because all runtime network access is forbidden.
- `gofmt -d catalog/sources/go-nanoid/harbor/controls/control-api.go`: exit 1
  because the pre-existing control stub is not gofmt-normalized; this did not
  change the source or affect the blocker decision.
- `git diff --check`: exit 0.

## Remediation

`artifact-or-verifier` blocker: parent must locate or register a source archive
whose bytes hash exactly to the required archive digest and whose contents
correspond to revision `2ab893bb7af49f55a4180d22371fbe9f954203b4`. Parent may
then construct/register a private replacement Oracle bundle, recompile twice,
and run the complete fresh NoNetwork Oracle/control matrix. Do not authorize
GitHub, codeload, DNS, Go proxy, or any external service, and do not reuse the
pre-migration receipts in `production-evidence.json`.
