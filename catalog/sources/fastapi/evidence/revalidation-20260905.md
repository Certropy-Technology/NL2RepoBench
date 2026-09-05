# FastAPI instruction-migration revalidation blocker

- Task: `fastapi`
- Revalidation date: `2026-09-05`
- Expected current catalog source digest: `sha256:344c805f4e9bb007628618a221cd1f9399f86619260ca0901cfc12b8ac7d7ce8`
- Frozen upstream revision: `50113da16fec53b66b80d75e80a89296de4fa5a5`
- Lifecycle: unchanged at `controls-passed`.
- Historical `production-evidence.json`: unchanged; its receipts are not reused.

## Offline artifact check

The required private artifacts were checked only in the local content-addressed
artifact store. All three are absent:

| Artifact | Digest | Expected size | Relative CAS location | Result |
| --- | --- | ---: | --- | --- |
| Dependency lock | `sha256:8914f4ed51ca932d3d2d867ccaf68a0e63725d713d97b71e734e0b11ecbbc853` | 13050 | `.nl2repo/artifacts/private/sha256/89/8914f4ed51ca932d3d2d867ccaf68a0e63725d713d97b71e734e0b11ecbbc853` | missing |
| Verifier bundle | `sha256:f34ee54461d223107071914b027e5335b047d4973e8e486526239105d76dde6a` | 20480 | `.nl2repo/artifacts/private/sha256/f3/f34ee54461d223107071914b027e5335b047d4973e8e486526239105d76dde6a` | missing |
| Oracle bundle | `sha256:8d62af7e5c67e733d1b928b56f9376c9992d493ded030da98490fce569d177cd` | 36997120 | `.nl2repo/artifacts/private/sha256/8d/8d62af7e5c67e733d1b928b56f9376c9992d493ded030da98490fce569d177cd` | missing |

The check was performed with `test -e` against each exact relative CAS path,
without DNS, registry access, source-host access, or any other network request.

## Revalidation decision

This is an artifact-availability blocker, not a source, instruction, model, or
permanent lifecycle failure. No compile or Harbor run was started because the
dependency lock, separate verifier, and Oracle inputs cannot be resolved from
the local CAS. The existing generated projection and historical production
evidence remain unchanged.

## Remediation

Restore the three exact CAS objects with the declared sizes and SHA-256 values,
then validate the source digest and compile twice with the locked Python
toolchain and `--allow-private`. Inspect the Oracle payload for a local,
digest-verified source archive, run the complete NoNetwork Oracle/empty/stub/
forgery/offline matrix, and persist fresh source-local receipts before updating
production evidence or the generated projection. Do not authorize GitHub,
codeload, package registries, DNS, or any external service, and do not change
the frozen denominator or lifecycle solely to bypass this blocker.
