# go-colorable authoring provenance

- Frozen upstream: `https://github.com/mattn/go-colorable`, revision `8bf39a204f13f0cfcf86ab9b297c3d6e0668e54a` (`v0.1.15`).
- Source authority: the preinstalled module cache exposed the version Origin; the Oracle-only solve script fetched the exact commit and verified the normalized git archive digest.
- Source digest: `sha256:920a15ba309669f30091349025493e370edc0aeee39eec63642c2e44a848197a`.
- License: MIT, LICENSE SHA-256 `88a2379b3ca34bf5c57127aff9dcb802bbb60ece0805cdbda65b3bd115f971d9`.
- Runtime: Debian Bookworm, Linux/amd64, Go `1.26.5`, `CGO_ENABLED=0`, `GOWORK=off`, `GOPROXY=off`, `GOSUMDB=off`, `GOTOOLCHAIN=local`.
- Dependency closure: private Go module bundle `sha256:e80546b0cbc56f4ea49ad1d6cd8406226e26b02ed91d6bb54344dece3a75ef36`, 1,028,872 bytes. It contains exact `go-isatty v0.0.20` and `x/sys v0.29.0` vendored bytes plus a validated offline manifest.
- Baseline: upstream Linux tests collected 6 test functions across 2 packages and exited 0. `go vet ./...` exited 0.
- Adaptation: Windows-only console conversion and benchmarks are outside the fixed Linux profile. The Oracle rewrites only the Go directive to `1.26.5`; functional source bytes are otherwise fetched from the frozen commit.
- Verifier boundary: private `contract.sh` invokes the public bridge through the Go subprocess supervisor. The trusted process does not import candidate code.
