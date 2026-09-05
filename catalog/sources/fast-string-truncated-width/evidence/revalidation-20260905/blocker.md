# fast-string-truncated-width instruction-migration revalidation blocker

- Task: `fast-string-truncated-width`
- Revalidation date: `2026-09-05`
- Expected current catalog source digest: `sha256:b2318c9af05c01b5e79583d82cf95228d8c22779c6925b37e04041f2c6d72822`
- Frozen upstream archive digest: `sha256:910a980a127ca70626d2bc0dbe673601e7c65c8778548cd1c3f94472c59c2f79`
- Lifecycle: unchanged at `controls-passed`; this is not a lifecycle transition.
- Historical `production-evidence.json`: unchanged because its receipt paths point to an old non-durable authoring run tree.

## Completed checks

`uv run nl2repo task validate-source catalog/sources/fast-string-truncated-width` passed and reported the expected source digest. Harbor `0.21.0`, Node `24.19.0`, and npm `11.17.0` were inspected. All four private CAS artifacts were found in the parent CAS with matching declared sizes and SHA-256 values. All eight task-local control scripts passed `bash -n`.

## Deterministic production compiles

Both commands used the current source, `toolchain.node.lock.toml`, the private CAS at `.nl2repo/artifacts`, `--allow-private`, and no runtime network authorization:

```text
uv run nl2repo harbor compile catalog/sources/fast-string-truncated-width --output .nl2repo/revalidation-20260905-compile-a --toolchain toolchain.node.lock.toml --artifact-root .nl2repo/artifacts --allow-private
uv run nl2repo harbor compile catalog/sources/fast-string-truncated-width --output .nl2repo/revalidation-20260905-compile-b --toolchain toolchain.node.lock.toml --artifact-root .nl2repo/artifacts --allow-private
diff -rq .nl2repo/revalidation-20260905-compile-a/fast-string-truncated-width .nl2repo/revalidation-20260905-compile-b/fast-string-truncated-width
```

Both compiles exited `0`; `diff -rq` reported no differences. The generated bundle contains 86 files, has raw manifest SHA-256 `sha256:ddac5aea76abdc4fcb21491da7e1c34d79ca6b2affe8eba95cd7280cb62fa725`, and has canonical manifest digest `sha256:c02a823ce86386d58346c7410c333b4083e78e09c1157b3e1a57c77956ccfc9e`.

## NoNetwork blocker

The hash-bound Oracle artifact is `sha256:2988312115f70e5f8b7adb941b18eaa55bff738964057cf0edf9d7006ae595da`. Its `solve.sh` is 1,591 bytes with SHA-256 `sha256:58ef8157b438498dde7f835d992127aaccbfafa48af2ae7a3bfb8a1010a45d67`. The script executes `git fetch` from `https://github.com/fabiospampinato/fast-string-truncated-width` for revision `1d50ce0c1497c1399eed50f87926817587049358` at runtime before checking the source archive digest and creating `/workspace`.

This violates the revalidation NoNetwork contract. Harbor Oracle and all controls were not run; no Oracle, grading, network, collection, result, or failure receipt is claimed. No external host authorization was granted.

## Remediation

Register a replacement private Oracle bundle containing a local, revision- and archive-digest-verified payload, or replace `solve.sh` with a source-local immutable payload. Recompile twice against the replacement and run the complete Harbor `0.21.0` Oracle, empty, stub, forgery, hang, install-script, loader-hook, oversized-output, and offline matrix. Persist every receipt under this evidence directory before replacing production evidence. Do not grant `github.com`, reuse stale receipts, change the frozen denominator, or alter lifecycle state solely due to this artifact/verifier blocker.
