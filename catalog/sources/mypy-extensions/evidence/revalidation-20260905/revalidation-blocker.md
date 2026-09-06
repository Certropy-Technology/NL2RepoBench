# mypy-extensions revalidation blocker

- Queue source digest: `sha256:be72a67a7d90cb83447dd9cd30f6787ae35b44c478ff54bbeeaa6c1c94699422` (validated before this file was written).
- Frozen revision: `9fc7fe08c8e638cdd9bbf1aa9bf188aef4fd24ef`.
- Frozen source archive digest: `sha256:173418926199a751045892c046f5dcd1280f7f360ce6799ad49a54f2679af03e`.

All three declared private CAS objects were found in `<parent-private-CAS>` and matched their declared sizes and SHA-256 values. The exact records are in `artifact-payload.json`.

The generated task Oracle bundle was inspected offline. It contains only `solve.sh`; no source archive is embedded. The script performs a runtime `git fetch` from `github.com`, creates an archive in an ignored temporary location, verifies the frozen digest, and materializes `<workspace>`. This violates the task's required NoNetwork contract, so no Oracle, control, compile, replacement bundle, or receipt was run or claimed.

Lifecycle, `task.toml`, historical `production-evidence.json`, generated projection, and shared CAS are unchanged. Parent remediation is to recover and independently verify the exact frozen source archive, register a NoNetwork Oracle replacement, compile twice, and run fresh Oracle plus supported controls. Do not reuse historical receipts or authorize the source host.
