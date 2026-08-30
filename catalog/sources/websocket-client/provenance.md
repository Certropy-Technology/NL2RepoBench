# `websocket-client` Provenance

The candidate was frozen from `websocket-client/websocket-client` at the full
commit `26f1c6439eb71489f2c5a2869942e049b78c2e41`. The private authoring
checkout produced a deterministic `git archive --format=tar` with the
prefix `websocket-client/`, SHA-256
`dd31f1cc888e206078188aa1b208ec9ffdc887ed5108f49ed837ecba3ddeccb2`, and
931840 bytes. The repository contains 80 tracked files, including 21 tracked
test files, and
an Apache-2.0 `LICENSE` whose SHA-256 is
`d7ad8d0966aa363d45c7b16b0838cadcd51676acdf215ad967307d581b47872c`.

The frozen source uses `setup.py`, declares Python `>=3.10`, has no mandatory
runtime dependencies, and exposes the `wsdump` console entry point. The
upstream test run on the frozen checkout completed with 181 passed, 26
skipped, and 21 passed subtests; skipped tests require live network, TLS,
external processes, or platform-specific behavior.

The public inventory, deterministic scored contract, and hidden-leaf mapping
are recorded in `api-inventory.json`, `test-inventory.json`, and
`traceability.json`. The private verifier is stored only as a content-addressed
artifact referenced by `task.toml`.
