# Chalk source/runtime digest audit

The two tar digests describe different, intentionally named artifacts:

- `source_digest` in `task.toml` is the immutable upstream Git archive for
  revision `661317e6f91fe7c90306c2c48ea9354562ee9146`:
  `sha256:0b041959f2c9516006566ed834208aaccf765e8d20f1b39efd8727e2d3844d80`.
- `catalog/tasks/chalk/solution/source.tar` is the transformed Oracle
  workspace archive:
  `sha256:336796bb61234612d46f383f0b039875165fe1a7f58e91ae4929aef6dbe41703`.

The transform is defined in
`.nl2repo/authoring-work/repairs/chalk/create_artifacts.mjs`: it copies the
runtime `source/`, license, and README; removes development-only package
metadata; normalizes the package export; and creates the zero-dependency npm v3
lock used by the Oracle workspace. Therefore the Oracle workspace tar is not
expected to equal the full upstream Git archive. The pinned source digest must
not be replaced by the transformed runtime digest.

The production compiler for schema version 2.0 is the Node compiler. The
verified command is:

```text
uv run nl2repo harbor compile catalog/sources/chalk \
  --output /tmp/chalk-worker-compile \
  --toolchain toolchain.node.lock.toml \
  --artifact-root .nl2repo/artifacts \
  --allow-private
```

It exits zero without `--allow-incomplete`. Passing `toolchain.lock.toml`
selects an incompatible Python toolchain schema and fails validation; that is
a command-selection error, not source-authority drift.
