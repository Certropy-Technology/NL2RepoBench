# `funcy` instruction-migration revalidation blocker

- Task: `funcy`
- Revalidation date: `2026-09-05`
- Expected catalog source digest: `sha256:7a760e49eabfdc2b8da265f27300aa21b191ac53927167cc998e5bdcedf5206c`
- Network policy: `no-network` for agent, candidate, verifier, Oracle, and controls
- Lifecycle: unchanged at `controls-passed`
- Historical `production-evidence.json`: unchanged; its pre-migration receipts are not
  replaced by this record

## Offline CAS check

The exact private artifact references declared by `catalog/sources/funcy/task.toml`
were checked in the authorized parent CAS only. Every object is absent. No registry,
source host, DNS, or external service was contacted.

| Artifact | Expected digest | Repository-relative CAS path | Result |
| --- | --- | --- | --- |
| dependency lock | `sha256:089efaf118e36d6827593b3ae59897143e2cc618c5c3bd41361fbaa1c46ec29b` | `.nl2repo/artifacts/private/sha256/08/089efaf118e36d6827593b3ae59897143e2cc618c5c3bd41361fbaa1c46ec29b` | missing |
| verifier bundle | `sha256:d348504af1cd511b21b4ab8e075a66679906b7847c77870228b11ac81161ffed` | `.nl2repo/artifacts/private/sha256/d3/d348504af1cd511b21b4ab8e075a66679906b7847c77870228b11ffed` | missing |
| Oracle bundle | `sha256:9a14f46490d30429f42e7b9cf0fcb2d89623c7fd0451cba396c88d1dd4696f4b` | `.nl2repo/artifacts/private/sha256/9a/9a14f46490d30429f42e7b9cf0fcb2d89623c7fd0451cba396c88d1dd4696f4b` | missing |

The verifier and Oracle payloads are required to establish a separate verifier
boundary and a trusted reference. The dependency lock is required for the locked
build. Their absence is an infrastructure/artifact blocker, not evidence that the
task is unsupported.

## Checks completed

- `uv run nl2repo task validate-source catalog/sources/funcy` passed and confirmed
  the expected source digest.
- `uv run python scripts/validate_instruction_quality.py` passed.
- `uv run nl2repo task lint-network --tasks-root catalog/sources/funcy --strict`
  passed with no task findings.
- `uv run --frozen --project harbor-runner harbor --version` reported `0.21.0`.
- JSON/TOML parsing, shell syntax, hash/path/leak checks, and `git diff --check`
  passed for this source-local change.

## Not run

The compiler, deterministic byte comparison, Harbor Oracle, empty, stub, forgery,
and offline controls were not run because all three required private CAS objects
are unavailable. No new manifest, grading, collection, result, reward, or network
receipt is claimed. The generated task projection and historical receipts remain
untouched.

## Remediation

Restore the three exact private CAS objects at their declared digests and sizes,
then rerun source validation and two production compiles with the locked Python
toolchain, `--allow-private`, and no `--allow-incomplete`; require byte identity.
Inspect the Oracle payload before any run and execute the complete NoNetwork Oracle,
empty, stub, forgery, and offline matrix only after a current manifest exists. Do
not fetch replacement artifacts, authorize external hosts, lower the frozen
denominator, reuse historical receipts, or change lifecycle state solely because
this artifact blocker remains.
