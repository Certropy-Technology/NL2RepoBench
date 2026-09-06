# Revalidation blocker

- Task: `huggingface-hub`
- Source revision: `c6be77fb44d91f474da963e5ad6fce4801811027`
- Catalog source digest: `sha256:4fa914929806b1aa576bf6e1c5d222ee881dadef1a108e6bae0ee09b3dd34b1f`
- Frozen source archive digest: `sha256:64d379d7374b8afb92dbade7829d328982633d137941ea0aa088d17582e6294d`
- Failure class: `artifact-or-verifier`

The declared Oracle artifact was verified at its exact size and SHA-256, but its
payload inventory contains only `solve.sh`; no source archive is embedded. The
script performs a runtime GitHub clone, which is forbidden by this task's
NoNetwork policy. A fresh Oracle retry reached that script and failed with exit
128. The first attempt also recorded an independent Harbor
`EnvironmentStartTimeoutError` infrastructure failure and was not treated as a
model result.

Bounded local recovery searched the declared Oracle bundle, task-local evidence
and provenance, retained authoring stores, parent private CAS, and local package
or module caches. No exact bytes matching the frozen revision and archive
digest were found, so no replacement bundle was constructed and no source host
was authorized.

Fresh compilation was deterministic: two exit-code-0 compiles produced the
same 58-file manifest (`sha256:27bec09c7eee347b90b1fca8291baad29add96b5055b26f6df57184cb2c2a4ba`,
canonical digest
`sha256:d645b4875f46b94d8ec56d4a9e88588909f6cd07b7b1bed692272186f86eb53e`).
Fresh NoNetwork controls collected the frozen denominator for `stub` (1/40),
`forgery` (1/40), and `call-hang` (3/40); `forgery` grading remained verifier
owned. `install-hang` intentionally timed out during candidate installation
and produced 0/0.

Next step: obtain an exact local source archive for the frozen revision whose
bytes hash to the declared archive digest, register it in private CAS, update
the Oracle bundle binding, recompile, and rerun the complete Oracle and control
matrix. Do not downgrade lifecycle or reuse the prior production evidence.
