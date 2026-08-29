# openai authoring audit

This source freezes the Apache-2.0 upstream commit
`555ac487f450f24928d859478ea2f41b58906206` and a 36-leaf offline core SDK
contract. The public instruction describes observable behavior without copying
implementation or private assertions. Private verifier and Oracle bytes remain
content-addressed under `.nl2repo/artifacts` and are not part of the public
source tree.

The contract is intentionally narrower than the 173-file upstream test tree.
It covers Pydantic-compatible model construction/serialization, query-string
encoding, incremental synchronous/asynchronous SSE decoding, webhook signing
and parsing, client configuration/copy semantics, and injected in-memory HTTP
request behavior. A successful Oracle result will not imply upstream parity,
live API support, provider support, or publication approval.

The production compiler resolved the private lock, verifier, and Oracle bundles
without `--allow-incomplete`. The trusted Oracle fetches only the full frozen
commit from `github.com`, asserts both the resolved revision and the Git archive
SHA-256, and then installs that checkout. Harbor 0.21.0 produced a valid Oracle result
of 36/36 (reward 1.0). The empty workspace produced the allowed candidate
installation failure at reward 0.0, the importable stub passed 1/36, and the
forgery control passed 0/36 despite writing fake reward files. All four Harbor
runs recorded `public_network_available=false` for both hostname and numeric-IP
probes. A separate verifier-image probe terminated a malicious build backend
after a three-second wall timeout with exit code 20 and outcome `timeout`.

The checked-out OpenHands runtime tag currently resolves to image ID
`sha256:dbfa15a345a0ab167aa205e895b02c5a581c569fea71941ab64c3df4569ec123`,
not the toolchain-locked ID
`sha256:70525a5fbee81f4d202b7f7de14857fe78f961ce2ec3995efd1a4850e45c7ea5`.
This did not invalidate Oracle or verifier controls, but the integrator must
restore or relock the immutable model-agent runtime before any model Agent Run.
