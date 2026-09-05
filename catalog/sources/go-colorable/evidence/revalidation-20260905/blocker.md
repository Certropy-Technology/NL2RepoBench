# go-colorable instruction revalidation blocker

- Expected catalog content digest: `sha256:f185adf752530f75548145d4db19ea7ffafc5a86a8bc90d0859b8e9a54888615`.
- Actual catalog content digest: `sha256:f185adf752530f75548145d4db19ea7ffafc5a86a8bc90d0859b8e9a54888615`.
- Frozen source revision: `8bf39a204f13f0cfcf86ab9b297c3d6e0668e54a`, source digest `sha256:920a15ba309669f30091349025493e370edc0aeee39eec63642c2e44a848197a`.
- Oracle, module, and verifier CAS objects were each verified against declared size and SHA-256.
- Two production compiles passed with identical 725-file bundles. The current canonical manifest is `sha256:55e61c1be543c7914773717fe24c78a7b10eb1c8c46f5afeaef7edd15444c720`.
- The Oracle bundle contains only `solve.sh`; inspection confirms runtime `git fetch` from `github.com`.
- Offline local recovery checked the Oracle bundle, task-local evidence/projections, historical authoring locations, and the preinstalled v0.1.15 Go module cache. The cache has same Origin revision and 16 source files, but its module zip is not the declared Git archive bytes and does not match the source digest.
- No replacement private bundle was constructed or registered. Oracle and controls were not run, so no stale or unsupported receipt is claimed.

Failure class: `artifact-or-verifier`.

Next step: restore or register an exact source archive matching the frozen Git archive digest, then update only the private Oracle payload reference, compile twice, and rerun the complete NoNetwork Oracle/control matrix.
