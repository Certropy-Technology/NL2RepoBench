# Hatchling instruction revalidation blocker

## Classification

- task_id: `hatchling`
- revalidation date: `2026-09-05`
- lifecycle preserved: `controls-passed`
- queued instruction/source digest: `sha256:bbbcabe585a8aee7e294fdde15fc9330eaa220f623f358007b4c9cef46089d34`
- current validation source digest: `sha256:bbbcabe585a8aee7e294fdde15fc9330eaa220f623f358007b4c9cef46089d34`
- frozen upstream revision: `ed8e30bebf98f2fe4d70c18a32a50a8160c391cb`
- frozen backend archive digest: `sha256:b3acd9e2fcdc976fd53eaa6f496ea2e32ad380d5046ec1bd7514c82cca5692d7`
- failure class: `artifact-or-verifier-blocked`

The declared dependency lock, private verifier bundle, and private Oracle bundle
were checked against the parent CAS before any compile or Harbor command. All
three outer artifacts exist and match their declarations:

| artifact | CAS path | size | SHA-256 |
| --- | --- | ---: | --- |
| dependency lock | `PARENT_CAS/private/sha256/1c/1c65ec786efe51baa5f9ff90c60c963719c41216451db6f18842eb89ba231a42` | 1317 | `sha256:1c65ec786efe51baa5f9ff90c60c963719c41216451db6f18842eb89ba231a42` |
| verifier bundle | `PARENT_CAS/private/sha256/c0/c0254a2120208a601926f00aef1bf192b5bf7dae057b8b491d5056697c151576` | 40960 | `sha256:c0254a2120208a601926f00aef1bf192b5bf7dae057b8b491d5056697c151576` |
| Oracle bundle | `PARENT_CAS/private/sha256/12/12ca5c724acddde911ed75dc767b5525b3feda3f2f9874153ae60167ebd1e65f` | 10240 | `sha256:12ca5c724acddde911ed75dc767b5525b3feda3f2f9874153ae60167ebd1e65f` |

The Oracle bundle contains only `solve.sh`; its script initializes a temporary
Git checkout and fetches `https://github.com/pypa/hatch.git` at the frozen
revision. Runtime GitHub access is forbidden by this revalidation contract.

## Bounded local recovery

The following offline checks were run from the worker checkout or the parent
project volume. The first command validated the queued source digest before any
edit. The CAS check exited 0 and confirmed all three declared artifacts. The
Oracle bundle inspection exited 0 and listed only `solve.sh`. Searches of the
task-local evidence, historical authoring state, authoring archives, retained
runs, and local archive candidates found no file whose bytes could be proven to
match the frozen `backend/` archive digest. Two broad archive searches exceeded
their bounded 180-second and 300-second tool limits; they are recorded as
infrastructure timeouts, not as source equivalence.

```text
uv run nl2repo task validate-source catalog/sources/hatchling
exit: 0
result: source_digest=sha256:bbbcabe585a8aee7e294fdde15fc9330eaa220f623f358007b4c9cef46089d34; status=controls-passed

python3 <CAS existence, size, and sha256 check for task.toml private refs>
exit: 0
result: lock 1317/1317 bytes hash-ok; verifier 40960/40960 bytes hash-ok; Oracle 10240/10240 bytes hash-ok

tar -tf PARENT_CAS/private/sha256/12/12ca5c724acddde911ed75dc767b5525b3feda3f2f9874153ae60167ebd1e65f
exit: 0
result: solve.sh only; no source.tar, oracle-package, or installable source payload

find AUTHORING_ROOTS -type d -iname '*hatchling*'
exit: 0
result: task-local authoring state and archived source metadata were present; no frozen source payload directory was found

find AUTHORING_ROOTS -type f \
  \( -name 'source.tar' -o -name 'source.tar.gz' -o -name '*.tar' -o -name '*.tar.gz' -o -name '*.zip' \)
exit: timed out after 180 seconds
result: bounded historical archive search did not produce a hash match before the tool limit

find . -type f \( -name 'source.tar' -o -name 'source.tar.gz' \) -print0 | xargs -0 sha256sum | \
  rg b3acd9e2fcdc976fd53eaa6f496ea2e32ad380d5046ec1bd7514c82cca5692d7
exit: timed out after 180 seconds
result: bounded repository archive hash search produced no proven match before the tool limit

find AUTHORING_ROOTS -type f \
  \( -name 'source.tar' -o -name 'source.tar.gz' -o -name 'source.zip' -o -name '*.tar' -o -name '*.tar.gz' \) \
  -size 378880c -print0 | xargs -0 sha256sum | rg b3acd9e2fcdc976fd53eaa6f496ea2e32ad380d5046ec1bd7514c82cca5692d7
exit: timed out after 300 seconds
result: bounded size-and-hash search produced no proven match before the tool limit
```

## Remediation and next step

Do not compile, run Harbor Oracle, or authorize any source host for this
revalidation. The parent should recover a trusted local archive containing the
`backend/` subtree at revision `ed8e30bebf98f2fe4d70c18a32a50a8160c391cb`,
verify its exact 378880-byte archive and
`sha256:b3acd9e2fcdc976fd53eaa6f496ea2e32ad380d5046ec1bd7514c82cca5692d7`
digest, then register a replacement private bundle in shared CAS. After that,
the parent must recompile twice from the unchanged source and rerun the full
Oracle/control matrix against the new manifest. No task-local lifecycle or
production evidence was changed by this blocker.
