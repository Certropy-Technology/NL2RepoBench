# mdast-util-to-hast revalidation blocker

- Task: `mdast-util-to-hast` version `2.0.0`
- Queue/source instruction digest: `sha256:59c3e69d361e744ca817a45786b06002e65933702c498978dad793e830a038d7`
- Frozen upstream revision: `174795b21f7757fffb54dd8d5fb4012f4751f791`
- Frozen source archive: `sha256:587e4050147dc8730b15a6ceedd07866301c4309bcdf8856697bbb3ba96f7094` (225280 bytes)
- Classification: `artifact-path-blocked`

`validate-source` passed before mutation. The four declared private CAS objects were
found in the parent CAS and matched their declared sizes and SHA-256 values. The exact
generated Oracle bundle was inspected offline: it contains `source.tar`,
`package-lock.json`, and `solve.sh`; the source archive matches the frozen source digest,
and `solve.sh` has no runtime source-fetch or network command.

Two production compiles were then run with the locked Node toolchain, parent private CAS,
`--allow-private`, and no `--allow-incomplete`. Both produced 305-file byte-identical
manifests (raw `sha256:2b650c6344c6d4394946c5009a2a1c125ad83941ced22fc1bbc590b01dec735c`,
canonical `sha256:63d84e11b19e07c969b1ec0f840c4345c59469fd5df64a74ddf180fdb7e8cf83`).

The compiled projection is not safe to execute or accept: 16 npm cache debug-log files
contain absolute historical authoring-worktree paths. This is an artifact hygiene
failure, not a model or verifier result. The detailed hashes, payload inventory, and
compile metrics are in `artifact-payload.json`.

No Harbor Oracle or control run was started, and no receipt or score is claimed. Lifecycle,
`production-evidence.json`, generated projection, task metadata, and shared CAS were not
modified. Normalize/rebuild the npm cache bundle to remove authoring paths, register the
replacement in parent-owned CAS, compile twice again, then run fresh NoNetwork Oracle and
all supported controls against the new manifest. Do not reuse existing receipts.
