# Jinja2 instruction revalidation blocker

## Frozen input

- Queue source digest: `sha256:afdf90d071a2dc6cbdeb4172c311ee6940d28f7feffdbf47ffd851e7af44c96c`
- Instruction SHA-256: `ed52e9641ae282952ed23e13e74081ef5b7d0e0d3e091318c1aedc3158f76f77`
- Upstream revision: `5ef70112a1ff19c05324ff889dd30405b1002044`
- Required unprefixed git archive: 1,249,280 bytes,
  `sha256:61082a25b5f6e7c49a0e4c12d9aa6be8e684489e0d613dc14512e8ea0c001421`

The pre-change `validate-source` result matched the queue digest exactly. The
migrated instruction was preserved unchanged.

## Artifact and compile result

All three declared private artifacts are present in the parent CAS and match
their declared byte size and SHA-256. The verifier bundle contains one
17,445-byte `run.py`; it compiles successfully and executes candidate scenarios
through the subprocess candidate-client boundary.

Two production compiles used `toolchain.lock.toml`, the parent private CAS,
`--allow-private`, and no `--allow-incomplete`. They were byte-identical:

- raw manifest SHA-256:
  `b555822f8b1ee0a37190bc3e10d2d51b51a9276cdb1c59796d5742895ee78ba3`
- canonical manifest digest:
  `sha256:98046b2014f19b7e5d862e51dff8d19510cee29df413109d6a3c0ead9a3bc87d`
- manifest file count: 58

## NoNetwork blocker

The declared Oracle bundle is hash-valid, but contains only `solve.sh`. That
script performs a runtime `git clone https://github.com/pallets/jinja`, checks
out the frozen revision, creates the expected archive, and then verifies its
digest. It contains no local source payload. No source-host, DNS, registry, or
other network authorization is permitted in this revalidation.

A bounded trusted-local search covered current and retained generated runtime,
the old task-specific authoring worktree and run paths, retained session logs,
handoff/worktree-diff archives, exact-size local cache candidates, and
task-named Docker containers/images. No bytes matching the frozen archive were
found. Session logs confirm the historical run used a network clone but do not
contain the source bytes. The complete search inventory is in
`local-recovery-search.json`.

Harbor Oracle and controls were not run because they would either violate the
NoNetwork contract or produce receipts for an unresolved Oracle bundle. Old
receipts were not reused. The task lifecycle and existing production evidence
remain unchanged; this file records an instruction-revalidation blocker, not a
new lifecycle terminal state.

## Next unblock action

Recover the exact 1,249,280-byte archive from a trusted historical run or other
local frozen backup. Verify its SHA-256, then build an ignored Oracle bundle
containing that archive and an offline extraction script. The parent must
review and register the replacement bundle, update the artifact binding,
recompute the source digest, compile twice, and run a fresh Oracle plus the
full supported control matrix against the final manifest.
