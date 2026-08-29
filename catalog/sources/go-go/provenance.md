# go-go authoring provenance

- Upstream: `https://github.com/TheAlgorithms/Go`
- Revision: `5ba447ec5ff3d1213de65b92e726ee74c5d5cc19`
- Git tree: `1a7ced1fa12ae31e2771a8f870395d818b70e815`
- Git archive SHA-256: `b3c92e9e75f682b5543bf069e4c2fc8fce0eda7067639185bd92e686cc648507`
- License: MIT, `LICENSE` SHA-256 `77d6707839a16c78953ce11b9ce9be3ca8ffe4bb43fbef2cc47cbe713fee3bfe`
- Selected package: `github.com/TheAlgorithms/Go/conversion`
- Frozen toolchain: Go 1.26.5 on linux/amd64, pure Go, no external modules
- Baseline: three offline `go test -count=1 -json ./conversion` runs, each with 43 passed leaf events and no failures or skips

The full upstream `go test ./...` baseline was also probed once. It produced
2633 passed events, one skipped event, and one failing randomized
Diffie-Hellman subtest outside the selected package. That unrelated upstream
failure is excluded by package scope, not hidden by changing conversion tests.

The public bridge contains only typed operation mapping and serialization.
Expected values and assertion cases are stored in the private verifier artifact.
The Oracle fetches only the pinned revision, verifies the raw Git archive digest,
then rewrites the Go directive to the frozen 1.26.5 toolchain and materializes an
empty vendor closure before the offline verifier build.
