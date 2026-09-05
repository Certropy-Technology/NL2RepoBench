# Revalidation blocker

Revalidation for the post-instruction-migration source digest is blocked by
missing private CAS artifacts. This is an artifact/infrastructure failure, not
a source, candidate, verifier, or model result.

## Frozen identity

- Task: `autojump`
- Version: `0.2.0`
- Current source digest: `sha256:7df74bd4004ec8cb9d6af416a940e0164b50fb5fb71518598afa1277aef2ccd0`
- Required runtime: Harbor `0.21.0`, Python `3.12.4`, `no-network`
- Lifecycle remains unchanged as `controls-passed`; the prior receipts in
  `production-evidence.json` are not treated as current for this source digest.

## Missing artifacts

The parent private CAS audit found none of these declared references under
`/data/NL2RepoBench-integration-20260827/.nl2repo/artifacts`:

| Purpose | Digest |
| --- | --- |
| dependency lock | `sha256:4d1b711c52bd3262eee78e924c0bad63a34801bf2c0e7969745655fa564b56f5` |
| Oracle bundle | `sha256:54f24a030373c9af6d4dc06f77d97eaf017ad30a80714587e163305290b7af5c` |
| verifier bundle | `sha256:7e1cabf2ad9afb7feaffb4a1f27da38c3fa26e90b054bfd40ce9d381b0def5e6` |

## Commands and results

All runtime commands were intended to be offline. Source validation and
task-local network lint passed:

```text
uv run nl2repo task validate-source catalog/sources/autojump
-> passed; source_digest=sha256:7df74bd4004ec8cb9d6af416a940e0164b50fb5fb71518598afa1277aef2ccd0

uv run nl2repo task lint-network --tasks-root catalog/sources/autojump --strict
-> passed; error_count=0, warning_count=0
```

The first required deterministic compile was attempted with the current
toolchain and parent CAS:

```text
uv run nl2repo harbor compile catalog/sources/autojump \
  --output .nl2repo/revalidate-autojump-compile-a \
  --toolchain /data/pi-tmp/root/worktrees/pi-worktree-08e03454-e600-47c9-b3db-4998d425975e-0/toolchain.lock.toml \
  --artifact-root /data/NL2RepoBench-integration-20260827/.nl2repo/artifacts \
  --allow-private
-> failed before bundle generation: ArtifactStoreError: artifact is missing:
   sha256:4d1b711c52bd3262eee78e924c0bad63a34801bf2c0e7969745655fa564b56f5
```

Because compilation failed before a final manifest existed, the second
determinism compile, Harbor Oracle, and empty/stub/forgery/offline controls
were not run. No old receipt was reused and no runtime host was authorized.

## Remediation

Materialize and independently verify the three frozen blobs in the parent CAS,
including byte size, media type, and SHA-256 against `task.toml`. Then rerun
both deterministic compiles, verify the final manifest and projection, and run
one fresh Harbor Oracle plus the complete control matrix under NoNetwork.
Only after those gates pass should `production-evidence.json` and lifecycle
evidence be updated to the new manifest digest.
