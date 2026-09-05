# anytree instruction-migration revalidation blocker

Date: 2026-09-05
Task: `anytree`
Version: `0.2.0`
Expected current source digest: `sha256:1ca33d77ee0d2f444687380887e282ef017fea7468dbcb83c80647976379b8f4`
Network policy: `no-network`

## Completed checks

- `uv run nl2repo task validate-source catalog/sources/anytree` passed and
  reported the expected current source digest.
- `uv run python scripts/validate_instruction_quality.py
  --sources-root catalog/sources/anytree` passed.
- `uv run nl2repo task lint-network --tasks-root catalog/sources/anytree
  --strict` passed with zero findings.
- `uv run --frozen --project harbor-runner harbor --version` reported
  `0.21.0`.

## Failed local-only compile

The required private CAS objects are absent from the supplied parent artifact
root. No registry, source host, DNS, or external service was contacted.

| declared asset | digest | local CAS path | result |
| --- | --- | --- | --- |
| dependency lock | `sha256:9bbdacc0a37d970d48fc387c12dbffb9f69b030e0ae87dfe9cd0415494643667` | `private/sha256/9b/9bbdacc0a37d970d48fc387c12dbffb9f69b030e0ae87dfe9cd0415494643667` | missing |
| verifier bundle | `sha256:a685f107c95260e9218d5a3034bb77cabe74f78aeb98f25f1bd6e6e778f4bbdd` | `private/sha256/a6/a685f107c95260e9218d5a3034bb77cabe74f78aeb98f25f1bd6e6e778f4bbdd` | missing |
| Oracle bundle | `sha256:dede9730f20ed93e4114a6425ce14f7b9443ac161d7d66fc4994287b70021395` | `private/sha256/de/dede9730f20ed93e4114a6425ce14f7b9443ac161d7d66fc4994287b70021395` | missing |

Command, from the isolated task worktree:

```text
uv run nl2repo harbor compile catalog/sources/anytree --output .nl2repo/anytree-revalidate-1 --toolchain toolchain.lock.toml --artifact-root /data/NL2RepoBench-integration-20260827/.nl2repo/artifacts --allow-private
```

Exit code: `1`.

Failure: `ArtifactStoreError: artifact is missing:
sha256:9bbdacc0a37d970d48fc387c12dbffb9f69b030e0ae87dfe9cd0415494643667`.
The compile stopped before generating a new bundle, so the second deterministic
compile, Harbor Oracle, and controls were not run.

## Stale projection evidence

The checked-in `catalog/tasks/anytree` projection still contains the previous
instruction bytes: source instruction size `21439`, generated instruction size
`18114`, and generated instruction SHA-256
`sha256:73f8e762bc63982f4e3655ec8a421233199c94f064298dea47af78d106d5a209`.
It must not be used as the current post-migration manifest.

## Remediation and next step

Restore the three frozen CAS objects from the parent private artifact store,
verify each byte count and SHA-256 against `catalog/sources/anytree/task.toml`,
then rerun both deterministic compiles with `--allow-private`. Only after a
new manifest exists may Harbor 0.21.0 Oracle and the complete empty/stub/
forgery/offline matrix be executed and canonical production evidence updated.
No lifecycle transition, denominator change, or receipt reuse was performed.
