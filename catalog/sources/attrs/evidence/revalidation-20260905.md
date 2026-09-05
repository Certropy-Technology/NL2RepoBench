# attrs instruction-migration revalidation

Observed at `2026-09-05T03:25:33Z` in the task-local revalidation worktree.
This is a source-local infrastructure/artifact blocker record. It does not
change `task.toml` lifecycle status, and it does not make the historical
`production-evidence.json` receipts current.

## Current source

- Task: `attrs` version `0.1.0`
- Expected current source digest: `sha256:c5104ce2cca70c4a1051a2b68554e46b52da247187d8bb826521dac50a4405c9`
- `uv run nl2repo task validate-source catalog/sources/attrs`: exit `0`; reported the expected digest and status `controls-passed`.
- `uv run nl2repo task lint-network --tasks-root catalog/sources/attrs --strict`: exit `0`; zero errors and zero warnings.
- Instruction SHA-256: `sha256:ad7d60658643532c9f9fb68bc31ef974eb0b01eb0deab8857baa93de81d6e7da`

## Revalidation attempt

The required deterministic compile command was attempted with the parent CAS:

```text
uv run nl2repo harbor compile catalog/sources/attrs \
  --output .nl2repo/attrs-revalidation-compile-a \
  --toolchain /data/pi-tmp/root/worktrees/pi-worktree-51c9c41d-9ed5-476f-93aa-4cdf08cb450f-0/toolchain.lock.toml \
  --artifact-root /data/NL2RepoBench-integration-20260827/.nl2repo/artifacts \
  --allow-private
```

Result: exit nonzero before bundle generation. The compiler reported:
`ArtifactStoreError: artifact is missing:
sha256:1cf14dce7bdbfee65cfc65d14a519fa3084f0b9e09223a6e8668225f6610c201`.
The second deterministic compile and all Harbor runs were not attempted because
the final manifest cannot be produced without the declared private artifacts.

The following exact CAS paths were checked and were absent:

```text
/data/NL2RepoBench-integration-20260827/.nl2repo/artifacts/private/sha256/19/193fc637b9876ef82979e422b12dc77a761387a303831c886c122e1fc6d0e0cb
/data/NL2RepoBench-integration-20260827/.nl2repo/artifacts/private/sha256/1c/1cf14dce7bdbfee65cfc65d14a519fa3084f0b9e09223a6e8668225f6610c201
/data/NL2RepoBench-integration-20260827/.nl2repo/artifacts/private/sha256/24/24eddf2b30290557b4cbe0408595fc9e1083c948bf97fbf06172f3def30ed932
```

Missing declarations:

- verifier bundle: `sha256:193fc637b9876ef82979e422b12dc77a761387a303831c886c122e1fc6d0e0cb`
- dependency lock: `sha256:1cf14dce7bdbfee65cfc65d14a519fa3084f0b9e09223a6e8668225f6610c201`
- Oracle bundle: `sha256:24eddf2b30290557b4cbe0408595fc9e1083c948bf97fbf06172f3def30ed932`

## Gate state

- Current final manifest: unavailable; no new manifest digest exists.
- Oracle: not run; no current `valid`, collection, reward, or network receipt.
- Empty/stub/forgery/offline controls: not run; no current control receipts.
- Historical receipts in `production-evidence.json`: stale after the public instruction migration and not reused.
- Failure class: `infrastructure` / missing private CAS artifacts.

## Remediation

Parent integration must materialize and digest-verify the three declared private
CAS artifacts in the authorized artifact store, then compile twice from this
source and rerun the complete NoNetwork Oracle and control matrix. Do not fetch
from a registry or source host, synthesize replacement artifacts, lower the
denominator, or update lifecycle/evidence to claim success before those gates
complete.
