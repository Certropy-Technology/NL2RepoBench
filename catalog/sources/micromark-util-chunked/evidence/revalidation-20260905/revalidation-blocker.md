# micromark-util-chunked revalidation blocker

- Task: `micromark-util-chunked` version `2.0.0`
- Queue/source digest: `sha256:971c3c9049d98c0e7a1e9ee175022ea2d980051202e938916f9f1b19812e4a6d`
- Frozen revision: `774a70c6bae6dd94486d3385dbd9a0f14550b709`
- Frozen source archive digest: `sha256:ffbc51c1237344db6b47db8000aaa1668e89eb207f6a94b3a5b6472d5dda08d1`
- Failure class: `artifact`
- Lifecycle and historical `production-evidence.json` remain unchanged.

## Bounded offline checks

`validate-source` passed and matched the queue digest. The generated runtime contains
`solution/source.tar`, 1,116,160 bytes, with the exact frozen source digest. Its
`solution/solve.sh` verifies that digest and extracts the archive; bounded inspection
found no runtime source-fetch or other network command. Details are in
`oracle-payload.json`.

The parent private-CAS root was checked for each declared dependency, commands, tests,
and Oracle artifact. None of the four exact digest/size pairs was available for
verification. Details are in `artifact-check.json`. Because a required artifact is
missing, no compile, Oracle, control, or receipt reuse was attempted.

## Remediation

Restore or register the four declared CAS objects, verify exact bytes and sizes, then
compile twice with the locked Node toolchain and run fresh NoNetwork Oracle, empty,
stub, forgery, and offline controls against the resulting manifest. Do not authorize
registries, GitHub, codeload, DNS, or any external service, and do not reuse historical
receipts. All future evidence paths must remain repository-relative or use placeholders.
