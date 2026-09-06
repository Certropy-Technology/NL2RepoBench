# mdast-util-mdxjs-esm revalidation blocker

- Task: `mdast-util-mdxjs-esm` version `1.0.0`
- Queue source digest: `sha256:366da4c3f17463f7598d4d4bc971c2c6fa5bf10459cec3ba12262dc945b6d3a3`
- Frozen revision: `8d05c28d15ec5b690e7fbb08d703b0752d431109`
- Frozen source archive digest: `sha256:a05b484b17c05730094d3b2f2458562a48d6b76fac39dcc2b7bfc5d9a33c4f87`
- Classification: `artifact-verifier` blocker for this revalidation pass

`validate-source` confirmed the queue digest. All four declared private CAS artifacts
matched their exact declared sizes and SHA-256 values; see `artifact-check.json`.
The exact generated-task Oracle bundle was inspected offline. It contains only
`adapter.js`, package metadata/lock data, and `solve.sh`; it does not contain the
frozen source archive. The script performs a runtime GitHub clone and archive fetch,
which is forbidden by this task's NoNetwork contract. Details are in
`oracle-payload.json`.

No compile, Oracle, control, receipt, score, or validity result is claimed. No host
authorization was granted, and historical production evidence, lifecycle metadata,
generated projection, and shared CAS were left unchanged.

## Remediation

Recover or parent-register an exact source payload whose archive bytes match the
frozen revision and digest, then construct a NoNetwork Oracle bundle and run double
compile plus fresh supported controls against the new manifest. Do not reuse any
historical receipt or restore network authorization.
