# css-tree Instruction Revalidation Blocker

- Task: `css-tree`
- Revalidation date: 2026-09-05
- Expected current catalog source digest: `sha256:7cd95806ac20f80ff1c7039645e7b3d262260043fa126c4f88f11cbc70978588`
- Source validation: passed; the CLI reported the expected digest and version `1.0.0`.
- Prior lifecycle: `controls-passed`; unchanged.
- Historical `production-evidence.json`: unchanged because its receipt paths are not durable in this worktree.

## Compile evidence

The current source was compiled twice with the locked Node/npm toolchain, the
parent private CAS, and `--allow-private`:

```text
uv run nl2repo harbor compile catalog/sources/css-tree --output <temporary-output-a> --toolchain toolchain.node.lock.toml --artifact-root <parent-private-CAS> --allow-private
uv run nl2repo harbor compile catalog/sources/css-tree --output <temporary-output-b> --toolchain toolchain.node.lock.toml --artifact-root <parent-private-CAS> --allow-private
diff -rq <temporary-output-a>/css-tree <temporary-output-b>/css-tree
```

Both compile commands exited `0`, and the output trees were byte-identical.
The generated production bundle contains 146 files, with canonical manifest
digest `sha256:2f8ee84d8be11948d4b4e555e84ffb043d531b8fd31f8b61aa86a90d9d18e587`
and bundle manifest file SHA-256
`sha256:62b736dbb16b6ae7aead8d2ca82f00cc661a66b72fe3026e04bd0a378da790c9`.
The compact compile records are tracked in
`revalidation-20260905/compile-a-summary.json` and
`revalidation-20260905/compile-b-summary.json`.

## Artifact closure

The parent CAS probe verified the declared size and SHA-256 for all four
private inputs: the npm dependency bundle, command plan, test bundle, and
Oracle bundle. Details are tracked in `artifact-closure-summary.json`.

## Blocker

The hash-valid Oracle artifact
`sha256:88cd55254a577f2cec7641465478f2e0f31e1ce0d048a3e1afebf554faf7d27c`
contains `solution/solve.sh`, which invokes `solution/fetch-source.mjs`.
That script performs `node:https.get()` against the codeload URL for revision
`88e3d965c0b1628642a30a841745b410d6835052` before verifying and extracting the
source archive. This violates the assigned NoNetwork contract. No Oracle or
control Harbor run was started, and no reward, validity, collection, or test
leaf result is claimed. The inspected payload and network decision are
recorded in `oracle-bundle-summary.json` and `network-summary.json`.

The frozen collection remains 32 `node:test` leaves. Since no fresh run was
started, `collection-summary.json`, `result-summary.json`, and
`failure-set-summary.json` explicitly record `not-run` and an empty failure
set rather than fabricating receipts.

The full source-root network lint scanned 480 tasks with zero global errors and
zero css-tree findings. The full generated-root lint scanned 824 tasks and had
one unrelated historical global error, but zero css-tree findings and zero
css-tree errors. No direct single-task lint was used as evidence.

## Remediation

Replace the Oracle bundle with a local payload containing the exact frozen
source, verified against revision
`88e3d965c0b1628642a30a841745b410d6835052` and source archive digest
`sha256:8b568680478944896703c6bc412665f5abb0720efe9f39372d3cb66ffa7ad778`.
Register the replacement in private CAS, recompile the source, inspect the new
solver for runtime network access, and run fresh NoNetwork Oracle, empty, stub,
forgery, and offline controls. Persist all resulting grading, network,
collection/result, and failure-set summaries before changing production
evidence or lifecycle.
