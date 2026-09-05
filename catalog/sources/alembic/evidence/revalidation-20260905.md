# Alembic revalidation blocker (2026-09-05)

## Status

The public instruction migration is source-valid and compiles deterministically,
but the production revalidation is blocked by the frozen Oracle payload. The
task lifecycle remains unchanged (`controls-passed`); this record does not
replace or refresh the existing production evidence.

## Verified inputs

- Task/version: `alembic` / `1.19.2-r1`.
- Current source content digest from `uv run nl2repo task validate-source
  catalog/sources/alembic`: `sha256:02885f63ea0a214e99b60665ed57f8c704cf259a2d155d0068f5bfa8ae31ec71`.
- Frozen upstream archive digest declared by `task.toml`: `sha256:d152069190bef5403affcb73bd9b25cdeb34b4662a9bc8b70f9fe65968b72e72`.
- Current instruction bytes: `sha256:047b8bea8a0d550c5e4828ba095d1d6fe9eee5d55ce8504b75cabc7a44083b08`.
- Harbor version: `0.21.0`.

The source-local strict network lint completed with zero errors. All Alembic
control shell scripts passed `bash -n`, and `production-evidence.json` parsed
as JSON.

## Deterministic compile evidence

Both commands exited `0` using the current source, `toolchain.lock.toml`, the
absolute parent CAS `/data/NL2RepoBench-integration-20260827/.nl2repo/artifacts`,
and `--allow-private`:

```text
uv run nl2repo harbor compile catalog/sources/alembic --output .nl2repo/revalidation/alembic-compile-1 --toolchain toolchain.lock.toml --artifact-root /data/NL2RepoBench-integration-20260827/.nl2repo/artifacts --allow-private
uv run nl2repo harbor compile catalog/sources/alembic --output .nl2repo/revalidation/alembic-compile-2 --toolchain toolchain.lock.toml --artifact-root /data/NL2RepoBench-integration-20260827/.nl2repo/artifacts --allow-private
```

The two generated bundles each contained 62 files and had the same aggregate
file digest `sha256:1c3f2c4eeb3a81a81bb3a86a68ed2fff44748f0caf349b62db19abe04fa48b8a`.
Their identical `bundle.manifest.json` digest was
`sha256:b80c35b9bc7d8f474579a6843ad08e8cbe6ad4ba8b8dbddb64eae4f48cc81c57`.
The new canonical manifest digest inside the generated task is
`sha256:dedf38cd51c02f4e8c6f26c51af3a2e445af13046b6ff6ccd88864ef3e0373f1`.
The checked-in `catalog/tasks/alembic` projection is still the pre-migration
projection and therefore is intentionally not claimed as matching this bundle.

## Blocker evidence

The Oracle CAS object is:

```text
.nl2repo/artifacts/private/sha256/4b/4b64c90e1a6b9daaaa5abc0726de8fb5c497aee7820bb6ec56271188491afa80
sha256:4b64c90e1a6b9daaaa5abc0726de8fb5c497aee7820bb6ec56271188491afa80
```

Its tar listing contains only `solve.sh`. The extracted script has SHA-256
`sha256:c601a5e1a1e870ffc6a0c8db6114c9cf733f49fb70aeadb210a13d6fbc41efdb`
and performs a runtime fetch from `https://github.com/sqlalchemy/alembic` with
`git fetch --depth 1 origin c116cbc0f39d9df2b4ce5f1871043a622ca8774f` before
checking the archive digest. No artifact in the parent CAS has SHA-256
`d152069190bef5403affcb73bd9b25cdeb34b4662a9bc8b70f9fe65968b72e72`.

The required NoNetwork Oracle run was therefore **not started**, and no stale
Oracle/control receipt was reused. Running the current solver would require
forbidden source-host authorization and would not validate the current
manifest. Empty, stub, forgery, and offline controls were likewise not run
against the stale checked-in projection.

## Remediation

Register a local, digest-verified Alembic source archive matching
`sha256:d152069190bef5403affcb73bd9b25cdeb34b4662a9bc8b70f9fe65968b72e72`
in the parent CAS, or replace the private Oracle payload with a locally
materializing solver whose inner archive is verified against that digest. Then
compile the current source projection again and run the one-attempt NoNetwork
Oracle plus the complete declared control matrix. Do not authorize GitHub,
reuse the old receipts, or lower the frozen denominator.

## Changed files

Only this source-local evidence file was added by this revalidation attempt.
No task metadata, instruction, generated runtime, verifier, control script, CAS
object, or shared report was modified.
