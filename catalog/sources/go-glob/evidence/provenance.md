# go-glob authoring provenance

- Candidate: `https://github.com/gobwas/glob`
- Frozen revision: `986c05fb7000e63414ddc61162d0067b7a1f5639`
- Source archive digest: `sha256:dcf7c3e6caf75b32e832bc6236e056904ae3d96ffc23904d0a1662b84a684a07`
- License: MIT; frozen `LICENSE` digest is recorded in `source-freeze.json`.
- Runtime: Debian Bookworm, Linux/amd64, Go `1.26.5`, `CGO_ENABLED=0`, `GOWORK=off`,
  `GOPROXY=off`, `GOSUMDB=off`, `GOTOOLCHAIN=local`.
- Dependency closure: standard-library-only private Go module bundle with a validated
  offline manifest and vendor marker.
- Baseline: upstream tests exited 0 across three packages; `go vet ./...` exited 0.
- Adaptation: the Oracle changes only the Go directive from `1.22.0` to `1.26.5` before
  running the frozen source tests. Functional source files and the commit assertion stay
  unchanged.
- Verifier boundary: private `contract.sh` invokes the public bridge through the Go
  subprocess supervisor. The trusted process does not import candidate code.
