# Deepmerge instruction revalidation blocker

## Status

The migrated instruction validates against source digest
`sha256:c6192af2d1323a2d4d8a254666b8c1bc99d9a0b12398f7773fa80b5fe763d4b9`.
Revalidation is blocked by a missing private npm dependency bundle. The task's
existing lifecycle and historical `production-evidence.json` are unchanged.

## Missing artifact

- Digest: `sha256:254f5f7dbff06a78cd543aa30f51ba20d7f78b67633f7157246c7b994239f20`
- Declared size: `390` bytes
- Declared media type: `application/vnd.nl2repobench.npm-bundle+tar`
- Expected CAS path (parent artifact store):
  `.nl2repo/artifacts/private/sha256/25/254f5f7dbff06a78cd543aa30f51ba20d7f78b67633f7157246c7b994239f20`

The commands artifact, private test bundle, and Oracle bundle were present and
digest-checked. Compilation was not attempted because the compiler must fail
closed when any private artifact is unavailable.

## Remediation

Restore the exact 390-byte artifact at the expected CAS path, verify its
SHA-256 and size against `catalog/sources/deepmerge/task.toml`, then compile
the current source twice with `toolchain.node.lock.toml` and the parent CAS.
Inspect the Oracle solver before any run; execute Oracle and every declared
control with no runtime network authorization, persist compact receipts under
this directory, and update production evidence only after all path/hash checks
pass. The required compile command is:

```text
uv run nl2repo harbor compile catalog/sources/deepmerge --output <fresh-output> --toolchain toolchain.node.lock.toml --artifact-root .nl2repo/artifacts --allow-private
```

## Evidence binding

- Validation log: `catalog/sources/deepmerge/evidence/revalidation-20260905/cas-preflight.log`
- Validation log SHA-256: `sha256:3436462e4a85642e5703a59d9be4eae8230dd6720605329fecd50cb665902017`
- No Oracle, control, or fresh bundle receipt is claimed by this blocker.
