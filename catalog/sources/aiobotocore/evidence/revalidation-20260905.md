# Instruction Revalidation Blocker

The public instruction migration changed the catalog content digest. The task
source validated at:

```text
sha256:195f243068e429821aaab4dbb4357d15bf93b62fd6bf12055367ccf39af6a10f
```

Two production compiles using the locked toolchain, `--allow-private`, and the
parent private artifact store completed deterministically. The fresh canonical
manifest digest was:

```text
sha256:064c17e017421861bdde369e7b27afcfd3c78e920d223589f176bbf052fac9ea
```

The current private Oracle payload requires a runtime GitHub fetch. The frozen
source archive required to materialize revision
`c92e345814ad97e5ec0633dbd34be5d26ee90dd3` is absent from the parent CAS:

```text
sha256:6118ac737ce18ff5e3ed0190e7cf8298a98ef2acd68e046f733050fe8934bc0d
```

No Oracle or control run was started because the revalidation contract forbids
network authorization for Agent, candidate, verifier, Oracle, and controls.
This is an artifact/verifier revalidation blocker, not evidence that the task
is unsupported. The lifecycle and prior production evidence remain unchanged
until the parent registers the exact archive, rebuilds a local-only Oracle
payload, compiles a new final manifest, and reruns the complete NoNetwork
Oracle/control matrix.
