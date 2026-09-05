# cachetools instruction-migration revalidation blocker

Date: 2026-09-05

## Scope and source validation

This is a task-local remediation record for the instruction-migration
revalidation. It does not change the lifecycle or replace the historical
`production-evidence.json` record. The source was validated with:

```text
uv run nl2repo task validate-source catalog/sources/cachetools
```

The command exited `0` and reported:

```text
task_id: cachetools
version: 1.0.0
status: controls-passed
source_digest: sha256:10a3e60289998e42b5796f61b48ae38a45b909a5c69f898578e51a0075a6c4d7
```

The expected catalog source digest therefore matches the current source. The
current source instruction also passes:

```text
uv run python scripts/validate_instruction_quality.py
```

## Missing private artifacts

The parent private CAS was checked offline using its content-addressed
`private/sha256/<prefix>/<digest>` layout. Both declared objects are absent;
neither size nor content could be verified:

| role | digest | declared size | CAS result |
| --- | --- | ---: | --- |
| separate verifier bundle | `sha256:10649f23624d72fa386488b7416b0c6eb6a3d34854de01bd6b51f1a234af7380` | 30,720 bytes | missing |
| Oracle bundle | `sha256:da5fc086e99abf5b3ea91e19f0dedb209eeec8aab999e595899fa0f445bbff3d` | 286,720 bytes | missing |

The offline probe checked the exact CAS paths and returned `MISSING` for both
objects. A local historical-path search found references to these digests but
did not produce either hash-verifiable payload. No network fetch was attempted.

## Commands and result

```text
uv run nl2repo task validate-source catalog/sources/cachetools
exit_code=0

uv run python scripts/validate_instruction_quality.py
exit_code=0

CAS_ROOT=<parent-integration>/.nl2repo/artifacts
for digest in \
  sha256:10649f23624d72fa386488b7416b0c6eb6a3d34854de01bd6b51f1a234af7380 \
  sha256:da5fc086e99abf5b3ea91e19f0dedb209eeec8aab999e595899fa0f445bbff3d; do
  hash=${digest#sha256:}
  test -f "$CAS_ROOT/private/sha256/${hash:0:2}/$hash"
done
exit_code=1 (the first missing object caused the bounded presence probe to fail)
```

The exact independent presence check reported `MISSING` for both digests. No
compile, Oracle, or control run was started because the verifier and Oracle
bundles required to construct a final closed-world task are unavailable. This
is an infrastructure/artifact blocker, not a source, model, or verifier score.

## Remediation and next step

Restore the two exact private CAS payloads from the approved artifact source,
then verify each declared size and SHA-256 before retrying. After restoration,
run two deterministic production compiles with the locked Python toolchain and
the parent CAS, inspect the compiled Oracle for runtime network fetches, and
run fresh NoNetwork Oracle, empty, stub, forgery, and offline controls. Copy
compact grading, network, collection/result, and bundle-manifest receipts into
this task's tracked evidence directory before changing production evidence or
claiming revalidation success.

Until those payloads are restored and all fresh receipts are durable, the
previous lifecycle and historical production evidence remain unchanged.
