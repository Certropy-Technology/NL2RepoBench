# go-version authoring provenance

- Candidate: `https://github.com/hashicorp/go-version`
- Frozen revision: `e2b1b0b0c4b32767e1570ddce50dff79fdddf092`
- Source archive digest: `sha256:e79a0e175c9821ee538e9ca25a504bb15b4f445f8781a3208c4f7704c5448c12`
- License: MPL-2.0, frozen `LICENSE` digest recorded in `evidence/source-freeze.json`.
- Module path: `github.com/hashicorp/go-version`; upstream directive is Go 1.16.
- Source baseline: one offline Go test probe collected 35 passing test functions and no failures.
- Runtime adaptation: the public source has no third-party module dependencies. The Harbor
  candidate workspace is normalized to Go 1.26.5 with an empty vendor closure. The private
  verifier calls the candidate only through the reviewed typed bridge and custom-json-v1
  contract; hidden assertions and expected values are not in the public source.
- Risk review: pure Go, no cgo/unsafe/plugin/generate/workspace/submodule/network behavior.
- Oracle policy: `solve.sh` fetches only the frozen revision inside the trusted Oracle bundle,
  asserts the resolved SHA and archive digest, and runs the upstream tests. Candidate and
  verifier runs remain no-network.

The source tree intentionally contains the instruction, reviewed bridge, controls, and small
hash-bound inventory records. Oracle, verifier, and module bundle bytes are private CAS
artifacts and are not part of the public instruction or candidate image.
