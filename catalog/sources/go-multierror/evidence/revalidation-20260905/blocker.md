# Revalidation Blocker: Missing Frozen Oracle Source Payload

## Frozen Input

- Task: `go-multierror`
- Expected queue source digest: `sha256:bafd793183597ca8a5ea578206925674064d5e86789709d453efd52ec0c2cd51`
- `validate-source` result: the same source digest, task version `0.1.0`, exit code `0`
- Upstream URL: `https://github.com/hashicorp/go-multierror`
- Frozen revision: `6d4d48630db25c3c83fa83ecd41dd8438b82963c`
- Frozen source archive digest: `sha256:1baf79ff1d042dda283afc4223d47f28b4684361d0bfb338957e873db53aa773`
- Frozen source archive size: not declared in `task.toml`; no local bytes matching this digest were found
- Required runtime: Go `1.26.5`, Linux/amd64, `toolchain.go.lock.toml`
- Network policy: `no-network`; no source host or registry authorization was used

## Private Artifact Checks

All declared private artifacts were present in the parent-provided private CAS and matched their declared bytes:

| Role | Digest | Declared size | Observed size | SHA-256 check |
| --- | --- | ---: | ---: | --- |
| Oracle bundle | `sha256:7ba21afe19b788c3740749ac15d3e5200c4e9f0accd191687c99e02961526a03` | 10240 | 10240 | passed |
| Go module bundle | `sha256:2ca0816da8e279f8f5f504d85d7fe6e676e042817649adb02c821cd974b7ac87` | 10240 | 10240 | passed |
| Verifier bundle | `sha256:002d6af5c5cff592f4d579562328243fc1bc2f8a5de1178e9c7eb8af2d5ed518` | 10240 | 10240 | passed |

The Oracle bundle contains only `solve.sh`. Its script fetches the frozen revision from GitHub and verifies the resulting archive; it does not contain `source.tar` or an installable source payload. The module bundle contains only `go.mod`, `go.sum`, `module.manifest.json`, and empty `vendor/modules.txt`. The verifier bundle contains `contract.py` and `contract.sh`.

## Commands and Results

Commands were run from the isolated worker worktree unless a command contains an explicit absolute path.

| Command | Exit | Result |
| --- | ---: | --- |
| `uv run nl2repo --help` | 0 | passed; current CLI inspected |
| `uv run --frozen --project harbor-runner harbor --version` | 0 | `0.21.0` |
| `uv run --frozen --project harbor-runner harbor run --help` | 0 | current Harbor run options inspected |
| `uv run nl2repo task validate-source catalog/sources/go-multierror` | 0 | expected source digest matched |
| `sha256sum` and `stat` for the three declared CAS refs in the parent-provided private CAS | 0 | all three size/hash checks passed |
| `tar -tf` of the Oracle CAS ref | 0 | only `solve.sh`; no source archive |
| bounded search of CAS, retained runs, task-local evidence, historical handoffs, authoring archives/worktrees, and local payload names | 0 | no exact frozen source archive found |
| `uv run nl2repo harbor compile catalog/sources/go-multierror --output .nl2repo/go-multierror-revalidation-compile-a --toolchain toolchain.go.lock.toml --artifact-root <parent-private-cas> --allow-private` | 0 | compile succeeded |
| same compile with output `.nl2repo/go-multierror-revalidation-compile-b` | 0 | compile succeeded |
| byte comparison of the two compile outputs | 0 | 69 files, identical paths/sizes/bytes |

No Harbor Oracle or control was run after this revalidation compile. Running the current Oracle would require prohibited runtime GitHub access, so no network workaround was attempted.

## Failure Classification and Next Step

- Failure class: `artifact-or-verifier`
- Blocker: the current Oracle payload is not self-contained and the exact source archive for frozen revision `6d4d48630db25c3c83fa83ecd41dd8438b82963c` and digest `sha256:1baf79ff1d042dda283afc4223d47f28b4684361d0bfb338957e873db53aa773` is unavailable in the bounded local sources checked above.
- Remediation: obtain or restore bytes matching that exact archive digest and associate them with the frozen revision; register the verified payload in parent-owned CAS, update only the private Oracle artifact binding, compile the final bundle twice, then run the Oracle and all supported controls under NoNetwork.
- Current lifecycle and `production-evidence.json` were preserved unchanged.
- No generated `catalog/tasks/go-multierror/` projection was created or modified.
