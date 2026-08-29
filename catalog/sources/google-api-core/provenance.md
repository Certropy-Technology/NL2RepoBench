# google-api-core Authoring Provenance

## Source freeze

- Upstream: `https://github.com/googleapis/google-cloud-python`
- Package path: `packages/google-api-core`
- Revision: `082a99a2c4a3e8d5df28eaeab9b2c710dd4296d5`
- Package version: `2.35.0`
- Package subtree archive: 162 tracked files, 186 tar members, 1,351,680 bytes,
  SHA-256 `sha256:673b703e9c4d227ea29b4f1ad06aba4c7f872cbaa634424ceb08991b113d6b07`.
  The archive was generated from the detached revision in this lane.
- License: Apache-2.0. The package `LICENSE` bytes have SHA-256
  `sha256:cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`.
- No submodules.

## Environment and dependencies

The selected image is `python@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a` with CPython 3.12.14 on Debian 13.6 amd64. The dependency closure is generated with `uv pip compile --generate-hashes` and stored as a private lock artifact. It contains the package's five runtime dependencies, their transitive closure, setuptools and wheel; no wheelhouse is committed or used by the verifier.

## Scope and adaptation

The upstream package contains 65 Python implementation files plus `py.typed`
and transport-heavy surfaces. After adding pinned `pytest-asyncio==1.3.0` and
`pytest-mock==3.15.1` to the task-local authoring probe only, the frozen suite
collected 892 nodes and completed with 882 passed and 25 skipped; pytest
subtests account for the result count exceeding the collected node count. The
21-leaf production contract samples the deterministic core: client
metadata/options, datetime and path helpers, REST/protobuf serialization,
exceptions, retry/timeout policies, page iteration, universe endpoints and
version headers. Live services, gRPC channels, credentials files and background
consumers are excluded and cannot be reached by the no-network verifier.

## Handoff policy

The private verifier and Oracle solution are content-addressed under
`.nl2repo/artifacts`. No source archive, hidden test, verifier implementation or
Oracle bytes are copied into the public source directory. The source lifecycle is
`controls-passed`; the handoff remains `awaiting-agent-run` for model evaluation,
and no model Agent Run is started in this lane.

The install-hang control was executed through Harbor after remediation. Its build
backend timed out, the candidate process was killed, the verifier returned
`candidate-installation-failed` with reward `0.0`, and both public network probes
were false.
