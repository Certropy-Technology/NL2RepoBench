# yargs Harbor authoring source

This directory is the human-maintained source contract for the yargs
repository-generation task. `task.toml` pins the source, environment, private
artifacts, network policy, denominator, and Harbor resources. The generated
Harbor tree is compiler output and must not be edited directly.

The verifier uses a separate no-network image. It packs and installs the
candidate with npm's offline cache, validates the package tarball, and runs a
42-leaf deterministic `node:test` contract through a non-root subprocess
adapter. The Oracle alone receives `codeload.github.com` as a run-scoped host
and verifies the exact frozen source before building the reference workspace.

Production compilation:

```bash
uv run nl2repo harbor compile catalog/sources/yargs \
  --output .nl2repo/authoring-work/yargs/compiled \
  --toolchain toolchain.node.lock.toml \
  --artifact-root .nl2repo/artifacts \
  --allow-private
```

Trusted Oracle execution:

```bash
uv run --frozen --project harbor-runner harbor run \
  -p .nl2repo/authoring-work/yargs/compiled/yargs \
  -a oracle --allow-agent-hosts codeload.github.com
```

Do not pass the source-host override to a model Agent Run.
