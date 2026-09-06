# micromark-util-character revalidation blocker

- Task: `micromark-util-character` version `2.1.1`
- Queue source digest: `sha256:4bffd8d1369e197fbbe59799731b6f9b9cdb6da577740463fbfa4d476dba21c4`
- Frozen revision: `774a70c6bae6dd94486d3385dbd9a0f14550b709`
- Frozen source archive digest: `sha256:ffbc51c1237344db6b47db8000aaa1668e89eb207f6a94b3a5b6472d5dda08d1`
- Classification: `artifact/verifier`
- Lifecycle and historical `production-evidence.json` are unchanged.

## Bounded offline checks

`validate-source` passed and matched the queue digest. The dependency, commands,
tests, and Oracle artifacts were each found in `<parent-private-CAS>` and matched
their declared sizes and SHA-256 digests; the machine-readable records are in
`artifact-check.json`.

The generated task Oracle bundle was inspected without execution. It contains
only generated reference files and `solve.sh`; it does not contain the frozen
source archive. The script performs a runtime upstream `git fetch` for the
frozen revision and verifies the archive digest afterward. That acquisition path
is forbidden by this task's `no-network` policy, so no Oracle or control receipt
was created and no host authorization was used. Details are in
`oracle-payload.json`.

## Remediation

Recover and independently verify an exact source archive for the frozen
revision, then have the parent register a reviewed NoNetwork replacement Oracle
bundle in the private CAS. Compile twice with the locked Node toolchain and run
fresh Oracle, empty, stub, forgery, and offline controls against that new
manifest. Do not reuse historical receipts or alter the lifecycle, denominator,
generated projection, or production evidence for this blocker.
