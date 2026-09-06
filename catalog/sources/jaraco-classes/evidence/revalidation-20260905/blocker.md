# jaraco-classes Instruction Revalidation Blocker

Status: `blocked for revalidation` (`artifact/verifier`), not a lifecycle
transition. The task currently remains `controls-passed`; its existing
`production-evidence.json` is intentionally preserved because its original
receipts predate the instruction migration and reference ignored run paths.

## Frozen Inputs

- Task: `jaraco-classes`, version `0.1.0`
- Revision: `eeccd0b835bccf18353c44f4b35a1a27c9284fce`
- Expected post-migration catalog source digest:
  `sha256:182e2d9d1d67ac7ba0df83ce87ae2cc63c0c3f14e2b606ac6a2addbc42e792e2`
- Required immutable source archive digest:
  `sha256:4c3f9931ea112ae1f06448efe329ab40a700ed8f484cf32431e2cb66b7ddd28f`
- Runtime: CPython `3.12.14`, Debian 12 amd64, base image digest
  `sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a`
- Network policy: `no-network` for agent, candidate, verifier, Oracle, and
  controls.

The queue digest was validated before any source change:

```text
uv run nl2repo task validate-source catalog/sources/jaraco-classes
exit 0; source_digest=sha256:182e2d9d1d67ac7ba0df83ce87ae2cc63c0c3f14e2b606ac6a2addbc42e792e2
```

## Artifact Checks

All three declared private artifacts exist in the parent CAS and match both
declared size and SHA-256:

| artifact | digest | size |
| --- | --- | ---: |
| dependency lock | `sha256:a40aefe9af103356292f794e87b6982d86ab7c836c30eab2d66ccc1465921a4e` | 619 |
| verifier bundle | `sha256:45ba99ad81180cf9e985ed592740b08dc2b9c6492f11d5713295d82e322a51a3` | 20,480 |
| Oracle bundle | `sha256:38a7e07a2908cc3f9e23bd983b4c6bfee29ea7d7197f8bdfd303bf67a04bf601` | 10,240 |

The Oracle bundle contains only `solve.sh`. Its script downloads the frozen
revision from `codeload.github.com` with `urllib`; it contains no `source.tar`,
package subtree, or other installable payload. Running it would require a
source-host authorization and would violate this revalidation's NoNetwork
contract.

Structured search details and artifact checks are in:

```text
catalog/sources/jaraco-classes/evidence/revalidation-20260905/local-recovery-search.json
```

## Bounded Local Recovery

The following local searches hashed candidates and found zero exact matches for
the required source archive digest:

| scope | candidates hashed | result |
| --- | ---: | --- |
| generated projections and review worktree | 158 | 0 matches |
| retained authoring-live archives | 3,745 | 0 matches |
| worker handoff artifacts | 3,816 | 0 matches |
| private CAS | 1,104 | 0 matches |
| local uv cache | 333,315 | 0 matches |

The historical authoring session records that the archive once existed and
matched the required digest, but the corresponding file was cleaned up. Session
text is not an acceptable source payload, so no replacement bundle was built.

## Gate Decision

No compile was run because the compiler would only produce a runtime whose
Oracle still fetches source at execution time. No Oracle or control was run,
and no pre-migration receipt was reused. This is an artifact/verifier blocker,
not a model, source-behavior, or infrastructure score.

The parent can unblock this revalidation by registering a private bundle that
contains the exact source archive for revision
`eeccd0b835bccf18353c44f4b35a1a27c9284fce` with digest
`sha256:4c3f9931ea112ae1f06448efe329ab40a700ed8f484cf32431e2cb66b7ddd28f`.
The parent must then update the Oracle payload binding, compile twice, and run
the complete NoNetwork Oracle/control matrix against the new manifest. Until
then, preserve the current lifecycle and production evidence.
