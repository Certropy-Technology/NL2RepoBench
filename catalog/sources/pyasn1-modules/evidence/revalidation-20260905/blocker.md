# Revalidation blocker: pyasn1-modules

Status: artifact/verifier blocked after instruction migration.

The queue entry and the pre-mutation `validate-source` result both identify source digest `sha256:ae6a83037f6d1a52a3ba368fe28b332ef8f910f2232617c3cab683616211b4eb`. The declared lock, verifier, and Oracle CAS objects were independently checked by exact byte size and SHA-256 and all matched. The Oracle bundle contains only `solve.sh`; it has no frozen source archive and executes a runtime `git fetch` from GitHub for revision `02f9c577bcd0ad9fedfb0fd5dc598d323f7984bf`.

A bounded search across local CAS, generated projections, historical handoffs, archives, and caches found no file matching the frozen source archive (`1648640` bytes, SHA-256 `5f7359441c2f6c58f1ee04134963b6b4c333ed62e45fdd4cacbdad4f6225a967`). Because the run contract forbids GitHub and all external access, a fresh compile/Oracle/control matrix cannot be run truthfully from the available payloads. Existing production evidence is stale after the instruction change and was not reused or modified. Generated projection and lifecycle were not modified.

## Attempted commands and logs

- `uv run nl2repo task validate-source catalog/sources/pyasn1-modules` — exit 0; [validate-source.txt](logs/validate-source.txt)
- `uv run nl2repo task lint-network --tasks-root catalog/sources` — exit 0; [network-lint.txt](logs/network-lint.txt)
- exact CAS size/SHA-256 probe and bounded local payload search — exit 0; [payload-search.txt](logs/payload-search.txt)
- verifier/control syntax checks — exit 0; [syntax.txt](logs/syntax.txt)

## Skipped gates

Compile twice, fresh Harbor Oracle, empty, stub, forgery, install-failure, workspace-boundary, and offline controls were skipped because the exact frozen source payload is unavailable and the existing Oracle would require forbidden runtime GitHub access. Prior receipts were not treated as current.

## Remediation

Parent should recover or register an exact archive matching the declared source digest and size, replace the fetch-based Oracle payload without changing the frozen revision, then perform a double compile and a complete fresh NoNetwork matrix. No replacement payload or private artifact bytes are included here.
