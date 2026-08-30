# Authoring audit

This task is `author-one` for the frozen tiktoken 0.14.0 revision. The
upstream package is a native Rust/PyO3 project with remote encoding data. The
task deliberately scores a deterministic, local adaptation because Harbor
Agent and verifier phases have no egress. The adaptation retains the ranked
BPE and public Python API contracts, while excluding remote vocabulary
acquisition, optional blobfile, NumPy, and accelerator performance.

The only future source-host authorization belongs to a trusted Oracle solve
script. `agent_network_mode` and `agent_allowed_hosts` remain no-network and
empty. No Harbor Agent Run is started from this lane.
