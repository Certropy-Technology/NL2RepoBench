# jsesc instruction-migration revalidation blocker

## Scope and source authority

- Queue source digest before changes: `sha256:1818e053bcda34fee24979f070fc5b2904df2a8ef5e554b5dceebb0598cfcb71`.
- `nl2repo task validate-source` returned the same digest before any tracked change.
- Frozen upstream revision: `203c8694d605b6f29d4c67d372897499ec4468fb`.
- Frozen Git archive: 81920 bytes, SHA-256
  `2f611c6a89206ce324ec112596b7aef0f76a22ddf402fb1960ac11be15532cce`.
- The migrated instruction hash is
  `sha256:d2628440a53dc166aeca96f7c2bc2d08dd3d0fe5cb56fb14326425b1b2c081c5`;
  old Oracle and control receipts bind a different instruction and are stale.

## Artifact and compile results

All four private artifacts match their declared sizes and SHA-256 values; see
`artifact-check.json`. Two production compiles using `toolchain.node.lock.toml`,
the parent private CAS, `--allow-private`, and no `--allow-incomplete` were
byte-identical. The migrated projection has 74 manifest entries, bundle
manifest SHA-256
`3b0db9eb0bbaa70173ad91cdfa442a06c603140745b11849b4ceba4843b736b0`,
and canonical manifest digest
`sha256:e02d530822bc1d10dba56d6b3416d1251b2a31cce2b7f9ce1af92d9f43e730f0`.

## Blocking condition

The Oracle artifact contains only `solve.sh`. At runtime it initializes a Git
repository and fetches the frozen commit from GitHub. It embeds no source
archive. The current revalidation contract forbids source-host authorization,
DNS, registry access, and all external services for Oracle and controls, so the
Oracle was not executed.

Bounded local recovery checked the generated runtime, retained supervisor
compile, task evidence, historical authoring claim/worktrees, handoff and async
archives, retained runs, local Git objects, and npm cache. The original
authoring work directory and exact source archive are absent. A cached npm
`jsesc@3.1.0` tarball was rejected because its bytes differ and its packument
`gitHead` is `819f534875fd87c9033bb72148ab6a6ad1219ca0`, not the frozen revision.
See `local-recovery-search.json` for the bounded search record.

## Classification and remediation

- Failure class: `artifact` / `oracle-payload`.
- Lifecycle and existing production evidence are preserved; no unsupported
  claim of a new Oracle or control result is made.
- No replacement bundle was constructed because no exact revision-bound local
  payload was found.
- Next step: recover the exact frozen archive (81920 bytes and the declared
  SHA-256), embed it in a private Oracle bundle, register it through the parent,
  update the artifact binding, compile twice, and run fresh Oracle, empty,
  stub, forgery, offline/no-egress, and supported robustness controls.
