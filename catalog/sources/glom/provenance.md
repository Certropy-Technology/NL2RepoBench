# glom Authoring Provenance

Status: `controls-passed`. The source contract is ready for integrator review and
the independent Agent Run loop. This lane did not start a Harbor Agent Run.

## Frozen Inputs

- Upstream: `https://github.com/mahmoud/glom`
- Revision: `30b477ab65560914a38f331614947d0894701044`
- License: MIT
- Source archive SHA-256: `2d63af893e86e1118fefb36f94323a1d09b3a4410132aca61f00d2f45d90e408`
- Runtime: CPython 3.12.14 on Debian 12 amd64
- Candidate dependency lock: `sha256:b3ab4f35abc257efe0ca5a002ef1e5164ea72147ea01a791f669ddf8fecb8a47`
- Verifier protocol: `custom-json-v1`, 28 deterministic leaves

The static inventory recorded 71 source files, 16 test files, and 182 test
definitions. A real pytest run over the frozen tree collected and passed 202
tests. The production denominator is intentionally the 28-case public
facade contract in the private child-side adapter. The adapter keeps Python
objects in the candidate subprocess and hashes normalized JSON observations.
The public instruction describes every scored behavior without exposing private
test bytes or implementation source.

## Remediation

The first production verifier probe collected all 28 leaves but every child
failed with `ModuleNotFoundError: No module named 'face'`. The task-local
private verifier rebuilt the child environment without the candidate dependency
path. The remediation added explicit propagation of
`NL2REPO_CANDIDATE_DEPENDENCIES` in `run.py` and inserted that path in
`adapter.py`; the verifier tar was rehashed and recompiled. The final Oracle
then passed all 28 leaves.

## Final Gate

The final production bundle is
`.nl2repo/compiled/glom-final/glom/bundle.manifest.json` with SHA-256
`416d0b32194d6dfcafefe6e2dce783ec7002fe5eac77bc104574a24c24fc84ea`.
Both generated images built successfully from the pinned base. Final manual
Docker verifier receipts are under
`.nl2repo/runs/glom-authoring-20260828/final-gate/`:

- Oracle: `valid=true`, `28/28`, reward `1.0`.
- Empty workspace: candidate installation failure, reward `0.0`.
- Stub: `28/28` collected, `0/28` passed, reward `0.0`.
- Forgery: `28/28` collected, `0/28` passed, verifier-owned reward `0.0`.
- Install timeout: bounded timeout, candidate failure, reward `0.0`.
- Offline: every final run used `--network none`; both hostname and numeric IP probes were false.

Machine-readable evidence is in `production-evidence.json`. The final source
validation and network lint logs are in `.nl2repo/evidence/glom/`; repository
network lint has 0 errors and no `glom` finding, with 139 pre-existing warnings
for other sources.
