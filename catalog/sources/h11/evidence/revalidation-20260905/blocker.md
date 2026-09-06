# h11 instruction revalidation blocker

- Task: `h11`
- Source revision: `62c5068c971579d61fa1b55373390e12f25fd856`
- Expected current source digest: `sha256:c39edc043ffca6306ae21ee56caf8a501dddfcd90f6120291919e84b462284a2`
- Failure class: `infrastructure`
- Exact local Oracle payload and all three declared private artifacts were found and hash-verified. The Oracle `source.tar` is `sha256:503ed1fbb3efd07a9145b2f5ed05169728319e75d8117a4ef986e3aa91ea33f4` and contains the frozen revision.
- Both deterministic Harbor compiles passed with identical manifest `sha256:cd5eab0ff5f2cfd767d616330628f777cce481d7f6422b0c6c1085a9f92f644a`. The source-local `empty.sh` control was added before compilation.
- The first Harbor command failed before creating a job: `Docker daemon is not running. Please start Docker and try again.` Exit code was `1`. No host authorization, network access, retry, or Docker cleanup was used.
- Oracle, empty, stub, forgery, and fresh offline receipts were not produced. Existing `production-evidence.json` and lifecycle status were not changed, because no current-manifest receipt is durable.

## Commands and results

1. `uv run nl2repo task validate-source catalog/sources/h11`: exit `0`; digest matched the queue.
2. `uv run --frozen --project harbor-runner harbor --version`: exit `0`; Harbor `0.21.0`.
3. `uv run nl2repo harbor compile ... --allow-private` twice with `toolchain.lock.toml` and the parent CAS: exit `0` both times; byte identity passed.
4. `uv run --frozen --project harbor-runner harbor run ... -a oracle ...`: exit `1`; Docker daemon unavailable.
5. One bounded retry of the same Oracle command: exit `1`; Docker daemon unavailable again.

## Next step

Make Docker available through the parent environment operation, then rerun the complete current-manifest Harbor matrix in fresh run roots. Do not reuse the historical receipts or amend `production-evidence.json` until durable repository-relative receipts are available.
