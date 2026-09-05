# cookie instruction revalidation blocker

Status: `revalidation-blocked` by missing private CAS artifacts. The task
lifecycle and historical `production-evidence.json` are unchanged
(`controls-passed`); this record does not assert a new Oracle or control gate.

## Source validation

- Task: `cookie`
- Expected catalog source digest: `sha256:8328c7748fcd3b96291aafa7b5c870bb61c9ffd28e3b8f26dc25880e14859ee1`
- Validation command: `uv run nl2repo task validate-source catalog/sources/cookie`
- Result: exit code `0`; reported source digest exactly matches the expected digest.
- Runtime constraint: Node `24.19.0`, npm `11.17.0`, Harbor `0.21.0`, `no-network`.

## Missing CAS artifacts

The following declared private artifacts were checked in the parent artifact
store without network access. Each expected content-addressed path is absent;
therefore size and byte-level SHA-256 verification cannot proceed.

| Role | Digest | Expected size | Checked path |
| --- | --- | ---: | --- |
| npm dependency bundle | `sha256:0465771fa2162c197c01e0fbf91097cb083e1d34df867386add3c2b9399c6d34` | 10240 | `.nl2repo/artifacts/private/sha256/04/0465771fa2162c197c01e0fbf91097cb083e1d34df867386add3c2b9399c6d34` |
| Oracle bundle | `sha256:6880843c56fbb2812265e32874ede71387f6a1559c240c785c25344fac2cc0fc` | 40960 | `.nl2repo/artifacts/private/sha256/68/6880843c56fbb2812265e32874ede71387f6a1559c240c785c25344fac2cc0fc` |
| test bundle | `sha256:fafcf9cc348d7b2d39d38862563860fc16e7dfb8968f01bd254453930bc08587` | 20480 | `.nl2repo/artifacts/private/sha256/fa/fafcf9cc348d7b2d39d38862563860fc16e7dfb8968f01bd254453930bc08587` |

The commands used for the no-network check were equivalent to:

```text
for digest in 0465771fa2162c197c01e0fbf91097cb083e1d34df867386add3c2b9399c6d34 \
  6880843c56fbb2812265e32874ede71387f6a1559c240c785c25344fac2cc0fc \
  fafcf9cc348d7b2d39d38862563860fc16e7dfb8968f01bd254453930bc08587; do
  test -e ".nl2repo/artifacts/private/sha256/${digest:0:2}/${digest}"
done
```

All three checks returned absent paths. No network, registry, GitHub, codeload,
DNS, or source-host authorization was used.

## Remediation and next step

The parent/integrator must restore or register the exact three artifacts in the
private CAS, preserving their declared sizes and SHA-256 digests. After that,
rerun `uv run nl2repo task validate-source catalog/sources/cookie`, compile the
source twice with `toolchain.node.lock.toml`, and require byte-identical
projections before running the Harbor Oracle, empty, stub, forgery, and offline
checks. Do not authorize runtime network access or reuse the historical
receipts, because the instruction migration invalidates their manifest binding.

No compile, projection regeneration, Oracle, or control command was run in this
attempt because the required artifacts were unavailable.
