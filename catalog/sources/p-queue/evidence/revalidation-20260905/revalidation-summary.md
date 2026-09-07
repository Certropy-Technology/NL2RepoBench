# p-queue instruction revalidation (2026-09-07)

## Classification

`infrastructure_pending`: the queue-declared source digest matches
`validate-source`, all four declared private artifacts match their exact local
CAS size and SHA-256, and two locked Node compiles produced byte-identical
manifests. The fresh Harbor Oracle could not start a trial because Harbor
0.21.0 returned `EnvironmentStartTimeoutError`; this is not a candidate or
model result. No Oracle score or control score is claimed.

## Verified inputs

- Queue source digest: `sha256:72ab2b57449aa935dfb297c920c8503e194053481bac0e7ad28442488e510160`.
- Frozen contract denominator: 46 leaves.
- Toolchain: `toolchain.node.lock.toml`; Harbor `0.21.0`.
- Fresh manifest: `sha256:379de129e9afa3814ab6d6265c74658a72b15054222773e9d59606a604f6517a`, 20,862 bytes.
- Repeat compilation was byte-identical and used neither `--allow-incomplete` nor network authorization.
- Artifact details and exact hashes are in `artifact-integrity.json`.

## Fresh Harbor attempt

```text
command: uv run --frozen --project harbor-runner harbor run -p <compiled-p-queue> -a oracle --job-name p-queue-revalidation-oracle-20260907 -o <oracle-run-root> --n-concurrent 1 --max-retries 0 --yes
exit_code: 1
classification: infrastructure
exception: EnvironmentStartTimeoutError
trials: requested=1 completed=0 errored=1 retries=0
```

The attempt ran from 09:54:58Z to 10:05:47Z and did not produce a verifier
trial, collection, grading, reward, or network receipt. The run was configured
for `no-network`; no source or registry host was authorized.

## Skipped matrix

Because the Oracle environment could not start, `empty`, `stub`, `forgery`,
`install-script`, `timeout`, and `offline` were not run. Their status is
explicitly `skipped-oracle-infrastructure-failure` in `oracle-result.json`.
No denominator was reduced and no stale receipt was reused.

## Remediation

Retry the Oracle once Harbor environment startup is healthy, compile a new
manifest for that run, and execute the complete supported control matrix. Until
then the prior `production-evidence.json` remains unchanged and this task is
not accepted as freshly revalidated.
