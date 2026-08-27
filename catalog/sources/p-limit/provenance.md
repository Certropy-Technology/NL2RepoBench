# `p-limit` Provenance

- Upstream: `https://github.com/sindresorhus/p-limit`
- Revision: `df476048d023ff868cd45b35ee47f5fb0ca2b25a` (`v7.3.1`)
- Archive digest: `sha256:87c578912149794beb4bd95f69199067eccab4a2b8867c95993b03187256f797`
- License: MIT; frozen license file digest
  `sha256:5c932d88256b4ab958f64a856fa48e8bd1f55bc1d96b8149c65689e0c61789d3`
- Locked runtime: Node `24.19.0`, npm `11.17.0`, Debian bookworm glibc
  `2.36`, `linux/amd64`
- Base image: `docker.io/library/node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`
- Upstream baseline: three fresh locked-image runs; each completed XO, 22 AVA
  tests, and tsd with exit code 0. XO emitted one non-failing TODO warning.
- Runtime closure: `yocto-queue@1.2.1`, npm lockfile v3, SHA-512 integrity,
  four cache files; clean `--network none` offline reinstall passed.
- Oracle: private digest-checked `git archive` plus a scripts-free package
  manifest and the same npm lock. The private archive is unavailable to the
  model agent and needs no run-time source egress.

The authoring clone and inventory are retained only under task-local
`.nl2repo/authoring-work/p-limit/`. Production compilation resolves immutable
private artifacts from task-local `.nl2repo/artifacts/`.

## Final authoring gates (2026-08-27)

- `uv run nl2repo task validate-source catalog/sources/p-limit` exited `0`.
- `uv run nl2repo task lint-network --tasks-root catalog/sources` exited `0`;
  p-limit contributed no error (the command reported unrelated warnings for
  other catalog tasks).
- Production compilation with `toolchain.node.lock.toml`,
  `.nl2repo/artifacts`, and `--allow-private` exited `0`. The deterministic
  output was written under `.nl2repo/runs/p-limit-production/compiled-final/`.
- Docker `29.7.2` built the final verifier image successfully from the pinned
  Node and Python image digests. Running that image with `--network none`
  against the digest-checked Oracle workspace exited `0` and produced
  `reward=1.0`, `test_pass_rate=1.0` for all 24 leaves.
- Direct final-bundle controls, all with verifier `--network none`, exited
  `0`: empty `0.0`, stub `1/24`, forgery `1/24`, install-script `0.0`,
  loader-hook `1/24`, offline `1/24`, and hang `0.0`. Receipts are in
  `.nl2repo/evidence/control-results.tsv` and the per-control directories
  below `.nl2repo/evidence/docker-control-*`.
- The focused Python foundation suite was attempted with `uv run pytest -q
  tests/test_node_foundation.py`: `37 passed, 11 failed` (exit `1`). The
  failures are environment-only: this detached worktree intentionally has
  pre-existing deletions of `harbor-runner/pyproject.toml` and
  `harbor-runner/uv.lock`, while the tests require that shared runner fixture.
  The task-local production compile and Docker verifier gates pass
  independently; the unrelated deletions were not restored or modified.

The final source status is `controls-passed` because the catalog schema does
not contain the handoff-only `awaiting-agent-run` state. The handoff records
that operational state separately. After this status update, source
validation and production compilation were rerun successfully; the final
bundle manifest has canonical digest
`sha256:b5eb8926e3d5fc5e706284b36f18f725ac8b5aa30c05510297f36aa835a16fd8`,
79 files, and zero manifest integrity mismatches. Syntax checks passed for the
private adapter/client and all shell entrypoints.
