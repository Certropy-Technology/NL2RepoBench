# Instruction revalidation blocker

- Task: `lines-and-columns`, version `1.0.0`.
- Queue source digest: `sha256:81b0aeab3dd8dc69e24faa91ce818321955055d4efda9a253e55b131436c00cb`.
- Frozen upstream revision: `eea2581b131685f2c21de777fd037c8ddd343354`.
- Frozen source archive digest: `sha256:ecd2011652df85d6d95d08e80d8d1d2ce06ac5dfcc9aca7ef3f28eace03c01f9`.
- Current instruction digest was checked against the queue before this evidence was added:
  `sha256:b9a5140e93a54f793ec15c8f0796db87dd4674d386e0afbeb3e89865a2c6f5b5`.

## Artifact checks

All four declared private artifacts were present in the parent CAS and matched both declared size and SHA-256:

| artifact | size | digest | result |
| --- | ---: | --- | --- |
| npm bundle | 10,240 bytes | `sha256:beddb6b453f8315cf2ea08b237ff6dd4bef26cc0c60e610acf1e17c9a807a887` | exact |
| command plan | 10,240 bytes | `sha256:e9338437d214111fee4790824bfc08ed1346a2519c1bcb439d53217221ed1040` | exact |
| test bundle | 10,240 bytes | `sha256:aa28d8707fda2c6e9667acbd4529610dd78116234c062a91877b41bc3a3d0a71` | exact |
| Oracle bundle | 10,240 bytes | `sha256:476c73cd585be59118622ae3b44707e58de11161c312d86158293c5f2e11e21e` | exact |

The Oracle bundle contains only `solve.sh`; it does not contain `source.tar` or another installable source payload.

## Bounded local recovery

The following trusted local locations were checked without network access:

1. Current private CAS and the checked-in `catalog/tasks/lines-and-columns/` projection.
2. Task-local `evidence/`, `harbor/`, and production evidence files.
3. Retained `.nl2repo/authoring-live/worktrees` and `.nl2repo/authoring-work` locations.
4. Historical session/handoff records and task-specific authoring logs.
5. Local npm, pnpm, and general cache locations.
6. A bounded hash scan of small task-related archives and source candidates.

No file matched the frozen archive digest, and no candidate replacement bundle was constructed. The original authoring worktree is absent; retained records contain the fetch-only script and metadata, not source bytes.

## Blocker

`catalog/sources/lines-and-columns/harbor/solution/solve.sh` performs a runtime GitHub fetch of the frozen revision. That is incompatible with the declared `no-network` policy for this revalidation. Compile and Harbor were intentionally not run because the Oracle source payload cannot be executed offline and no exact local replacement is available. Prior `production-evidence.json`, lifecycle status, and generated projection were preserved; no stale receipt was reused.

Failure class: `artifact-or-verifier`.

## Next step

Register an exact archive for revision `eea2581b131685f2c21de777fd037c8ddd343354` whose bytes hash to `sha256:ecd2011652df85d6d95d08e80d8d1d2ce06ac5dfcc9aca7ef3f28eace03c01f9`. Then replace the fetch-only Oracle payload, compile twice with the locked Node toolchain, and rerun the 34-leaf Oracle plus empty, stub, forgery, offline, and supported controls against the new manifest.
