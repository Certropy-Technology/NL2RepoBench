# Tokenizers authoring provenance

- Upstream: `https://github.com/huggingface/tokenizers`
- Frozen revision: `d5827816baedcbf1cb5b452dea8048150b6872df`
- Commit tree: `66236e7ea0531c9e76294112a46c80e6e8469f6b`
- Canonical unprefixed `git archive --format=tar HEAD` digest: `sha256:ee078d644cd1e414f7a27a3085124577584dccbdeb4bc3f0addc4b065bc4b2d1`
- License: Apache-2.0; `LICENSE` SHA-256 `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`.
- Package metadata: Python `>=3.10`, `maturin>=1.0,<2.0` build backend, runtime `huggingface_hub>=0.16.4,<2.0`, Rust crate `tokenizers-python` version `0.23.2-dev.0`.
- Binding inventory: 16 Python binding files and 1,479 nonblank/noncomment LOC; upstream binding test inventory is 19 files and 223 test functions, with network/platform cases excluded from the deterministic contract.
- Build probe: CPython 3.12.11, maturin 1.15.0, rustc/cargo 1.97.1 built `tokenizers-0.23.2.dev0-cp310-abi3-manylinux_2_34_x86_64.whl` (3,601,244 bytes) from the frozen source tree.
- Private verifier uses 32 fixed custom-json-v1 leaves and invokes candidate APIs only through the trusted subprocess client. Candidate cannot read private verifier/Oracle bytes or trusted reports.
- Large source, build, and probe material remains in `.nl2repo/authoring-work/python-author-wave2-20260828/tokenizers/`; only compact provenance and content-addressed refs are placed in this source.
