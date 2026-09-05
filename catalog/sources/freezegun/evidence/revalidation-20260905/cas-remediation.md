# Freezegun instruction revalidation blocker

Revalidation was checked against the expected catalog digest
`sha256:b62fef7e3dbb495976fa027b27f35727b47fd59aec1ce63778b3d163bcad58ec`.
The source archive digest declared by `catalog/sources/freezegun/task.toml`
remains `sha256:3ffdbdaf8a3b15a5d4a79608885e114ed8a2b3f72712301b2342c697bfd24823`.

The required private CAS objects are absent from the offline artifact store
`.nl2repo/artifacts`:

| role | digest | declared size |
| --- | --- | ---: |
| Oracle bundle | `sha256:0461dddad21fc9f5fd2830832f89abac505bd3bc0d0f671bb6bfbb374e6129bf` | 194560 bytes |
| dependency lock | `sha256:22b0ccfd39dfcf82a9b7367da41a8bd6be98b4ee365fbcd5839a02842205b884` | 1388 bytes |
| verifier bundle | `sha256:253bbf64c2964cad8a0f06e51dcd1a212da4bb62bbb68aceb657c654db3d4fe2` | 30720 bytes |

The exact offline probe checked each expected path under
`.nl2repo/artifacts/private/sha256/<prefix>/<digest>` and reported `MISSING`.
Because the dependency, verifier, and Oracle inputs cannot be hash-validated,
no compiler, Oracle, or control run was started. This also means no new
receipt, reward, collection, or network result is claimed.

The existing lifecycle, `production-evidence.json`, controls, and generated
projection were intentionally left unchanged. Remediation requires restoring
all three objects at their declared digests and then rerunning two deterministic
compiles followed by the complete NoNetwork Oracle/control matrix.
