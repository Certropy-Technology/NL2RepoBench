# Canonicalize instruction revalidation blocker

Revalidation was attempted after the instruction migration. The task source
validated successfully with catalog content digest:

```text
sha256:9976318697d71b38920fc4e5cf74bc5559cb1f90d66721b58746776d49baeac9
```

The immutable upstream source archive digest remains the distinct source-lock
value recorded in `task.toml` and `provenance.md`:

```text
sha256:7436a1cb393e1e1b577c0066f2d9f2bc71666943d3ae740c19fc0b8a5ec60403
```

## Missing private artifacts

The parent private CAS was checked at its standard
`artifacts/private/sha256/<prefix>/<digest>` layout. All four declared artifacts
are absent:

```text
sha256:1d0804c94875e62734e0cb6a78130282e77a0696b1d2ecee36d83878120d9488  test bundle
sha256:5edebff66c2e4b4bed40e1a3a4ab726d62511b3314442a24e2e08403afd292d9  Oracle bundle
sha256:911470dae44f1bcb844fd01523adf9f082db227f52e51d0695f2ad0a96ead73a  npm dependency bundle
sha256:cee1b3612813db19dbc6c5ef687b4cb81418b9376be2a3f431baf66a5f1c0097  command bundle
```

The observed metadata sizes are 10,240 bytes, 133,120 bytes, 4,321,280 bytes,
and 10,240 bytes respectively. No network fetch, registry access, DNS lookup,
source-host authorization, compile, Oracle run, or control run was attempted
after the missing-artifact precheck.

## Commands and results

```text
uv run nl2repo task validate-source catalog/sources/canonicalize
exit 0; source status packaged; catalog content digest matched the expected sha256:9976318697d71b38920fc4e5cf74bc5559cb1f90d66721b58746776d49baeac9

python3 <local CAS digest existence and SHA-256 check for all four declared artifacts>
exit 0; all four paths absent; no bytes were available to hash

uv run nl2repo task lint-network --tasks-root catalog/sources --strict
exit 1 because the full catalog has 198 historical warnings; target task_id=canonicalize had zero findings and zero errors

uv run python scripts/validate_instruction_quality.py
exit 0 for canonicalize
```

The task remains `packaged`; this is an artifact/infrastructure revalidation
blocker, not a claim that canonicalize is unsupported. The parent must restore
and verify the four exact CAS objects, compile twice with the locked Node
toolchain, persist repository-relative receipt summaries under this evidence
directory, and rerun the complete NoNetwork Oracle/empty/stub/forgery/offline
matrix before changing production evidence or lifecycle.
