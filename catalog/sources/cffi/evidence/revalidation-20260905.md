# Instruction Revalidation Blocker

The migrated catalog source validates at:

```text
sha256:2154275867c99c55801380154a85294714a5d3147d0b36a08a45271c9b593b26
```

Parent-side CAS inspection found that all three private artifacts declared by
this task are absent:

```text
sha256:4558565a0bd78b2b9a608107c09d299a183f6f254c333915837c31ce3857e3b5
sha256:97ae56223612c6d64d5b7941b01a049e66db26c7b88d17fd414efb4b5a35c601
sha256:e46f6b4e04c812094a23cdcf944d70a3b3d2b6516e111e0ff2b252325fe663e0
```

The expected files under `.nl2repo/artifacts/private/sha256/` were checked
without network access and were not present. A production compile, Oracle, and
controls cannot resolve their immutable inputs, so no run was attempted and no
historical receipt was reused.

This is an artifact/infrastructure revalidation blocker, not evidence that the
task is unsupported. The lifecycle and production evidence remain unchanged.
The next step is to restore and hash-verify the exact dependency, verifier, and
Oracle artifacts in the parent CAS, compile the final manifest twice, and run
the full NoNetwork Oracle/empty/stub/forgery/offline matrix.
