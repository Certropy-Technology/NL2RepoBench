# Revalidation blocker: missing verifier bundle

- task: `go-pterm`
- source digest validated before this change: `sha256:71b02953ed6509c94f98db5aac7757309e6607e0e2960174fba573d7bad26268`
- source revision: `bacb2fc434b361b8951d1c7649c2029b1d7b6a83`
- expected verifier bundle: `sha256:19613ffeac932cb4e608661b9be87021482abd6ef5b80b821c877f9aeb2cadf0`
- expected verifier bundle size: `1507` bytes
- failure class: `artifact`

## Offline artifact checks

The declared Oracle bundle and module bundle are present and hash-valid in the
parent CAS:

```text
oracle_bundle: exit=0, size=2106, sha256=16a496828951925f7c4e422b013ba250101b7713e3371f06c6dacd2d42169d01
module_bundle: exit=0, size=1835857, sha256=f2c548708a2e8fce5d83dca4048d4c7ffcdf02426137c0a6f833d841a8c69f48
```

The declared verifier bundle was checked at the parent CAS path
`.nl2repo/artifacts/private/sha256/19/19613ffeac932cb4e608661b9be87021482abd6ef5b80b821c877f9aeb2cadf0`:

```text
verifier_bundle: exit=1, missing; expected_size=1507; expected_sha256=sha256:19613ffeac932cb4e608661b9be87021482abd6ef5b80b821c877f9aeb2cadf0
```

Validation of the current source completed successfully:

```text
uv run nl2repo task validate-source catalog/sources/go-pterm: exit=0
queue source digest: sha256:71b02953ed6509c94f98db5aac7757309e6607e0e2960174fba573d7bad26268
```

## Scope and next step

No compile, Harbor Oracle, or control run was attempted. The existing lifecycle
and production evidence were preserved. The parent should recover or register
the verifier bundle at the exact digest and size above, then re-run the required
double compile and complete NoNetwork Oracle/control matrix against the new
manifest. This file is the only revalidation change for this task.
