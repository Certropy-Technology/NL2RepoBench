# lxml instruction revalidation blocker

The queue-authoritative catalog source digest is
`sha256:a847ba1ce6973be4a4eeeb649615f2af9559f4af034a405e1314a664954a5313`.
The required source revision is `36f11f9d5edca7e85d20102fa253c1dad42929ee`,
whose frozen archive digest is
`sha256:cac1e83f3fa07b77097da8f98cb58bd4b2bc3e6b5a55eb7b6c942ed1b0e66d29`.

## Checks performed

- `uv run nl2repo task validate-source catalog/sources/lxml` passed before any
  mutation and reported the queue source digest.
- All three declared private artifacts were checked offline by exact size and
  SHA-256. The lock, verifier bundle, and Oracle bundle matched.
- The generated lxml projection, retained local archives, private CAS, and
  historical task-local worktrees/handoffs were searched. No trusted file
  matched the frozen source archive digest.
- Two production compiles completed successfully and produced byte-identical
  temporary manifests. They are summarized in `compile-a-summary.json` and
  `compile-b-summary.json`.
- The compiled Oracle bundle was inspected before execution. Its only file is
  `solve.sh`, which initializes a Git repository and executes
  `git fetch --depth 1 origin <frozen revision>` from `https://github.com/lxml/lxml.git`.

## Classification and remediation

This is an artifact/verifier revalidation blocker, not a candidate or model
failure. Running the Oracle would violate the task's `no-network` policy, so no
Oracle or control receipt was created. The existing `task.toml`, lifecycle,
generated projection, and historical `production-evidence.json` were left
unchanged. The next unblock action is to recover or parent-register an exact
archive/replacement bundle whose inner source bytes prove both the frozen
revision and `source_digest`, then recompile and run the complete fresh matrix
under NoNetwork.
