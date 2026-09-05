# Coverage instruction revalidation blocker

Date: 2026-09-05

The instruction source validates at the expected post-migration digest
`sha256:905b1544bd4883cdc2bb6bc7c5e891b6d5dcd08f170f8c594546db7c3e442f4d`.
All three declared private artifacts are present in the parent CAS with matching
size and SHA-256. The task's existing generated projection and historical
production evidence were therefore not modified.

Revalidation is blocked at the Oracle payload boundary. The declared Oracle
artifact `sha256:2d45f7b66bb07b2dc39b7c3bf032721577cc97e0c38bf03f89588be6e688da90`
is a 10,240-byte POSIX tar containing only `solve.sh`. That script initializes a
Git remote at `https://github.com/coveragepy/coveragepy` and runs `git fetch` for
revision `aeaa79b812d1bc637ebb5582ab12c076e192c87e` before creating the source
archive. This violates the required NoNetwork runtime policy, so no Oracle or
control run was started from this payload.

## Remediation

Replace or rebuild the private Oracle artifact with a payload whose bytes are
bound to the frozen source revision and archive digest
`sha256:d4c34fff118dcfe6e22a637411cdd5c5a7605dd2e65ed510560637ee94467e56`.
The replacement must materialize that verified local archive without GitHub,
package registries, DNS, or any other external service at runtime. Then compile
twice from the current source and rerun the complete Oracle, empty, stub,
forgery, and offline matrix, copying all receipt summaries into this directory.

## Evidence

- Inspection log: `catalog/sources/coverage/evidence/revalidation-20260905/oracle-payload-inspection.log`
- Inspection log SHA-256: `sha256:957659ee5e29a66fc1356ae7c2c1850a7f0e8363a85f2c6c03e7f546fd8576ba`
- Source validation command: `uv run nl2repo task validate-source catalog/sources/coverage`
- Source validation result: passed; digest matched the expected post-migration digest.
