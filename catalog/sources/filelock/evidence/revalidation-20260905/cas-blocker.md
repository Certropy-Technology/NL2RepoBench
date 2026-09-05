# Filelock instruction-migration revalidation blocker

- Task: `filelock`
- Revalidation date: `2026-09-05`
- Expected catalog source digest: `sha256:64024a3ae1a5e70bcf9816693b52e372c1f5f5ab8fa20aeacfe92fc89276fd07`
- Confirmed catalog source digest: `sha256:64024a3ae1a5e70bcf9816693b52e372c1f5f5ab8fa20aeacfe92fc89276fd07`
- Lifecycle: unchanged at `controls-passed`.
- Historical `production-evidence.json`: unchanged. No revalidation result replaces its existing receipts.

## Blocker

The current parent CAS does not contain the three private artifacts required to
revalidate this task:

| Artifact | Declared size | Canonical repository-relative CAS path |
| --- | ---: | --- |
| Verifier bundle `sha256:36d03a7f2840b4a6cd4d22576dc52f0479aa1b00c6ddef85fd07cc59cba4d903` | 30,720 bytes | `.nl2repo/artifacts/private/sha256/36/36d03a7f2840b4a6cd4d22576dc52f0479aa1b00c6ddef85fd07cc59cba4d903` |
| Oracle bundle `sha256:79d7adb06dd589461714a73ddabe6f8157d70dcded43aa3c89563b2a4b7f3b0d` | 1,556,480 bytes | `.nl2repo/artifacts/private/sha256/79/79d7adb06dd589461714a73ddabe6f8157d70dcd43aa3c89563b2a4b7f3b0d` |
| Dependency lock `sha256:883ffff65a1fe5256972090cc49ca607098dddaec0c4b6089f8192d9abb7b679` | 1,890 bytes | `.nl2repo/artifacts/private/sha256/88/883ffff65a1fe5256972090cc49ca607098dddaec0c4b6089f8192d9abb7b679` |

All three canonical paths were absent, and an exact-name search found no copy
of any digest elsewhere under `.nl2repo/artifacts`. Without these objects the
private verifier, hash-locked build closure, and Oracle cannot be materialized.
This is an artifact/infrastructure blocker, not evidence that the task is
unsupported and not a lifecycle transition.

## Checks performed

The checks were performed from the repository root with runtime network access
disabled by policy. The CAS probe emitted:

```text
missing 36d03a7f2840b4a6cd4d22576dc52f0479aa1b00c6ddef85fd07cc59cba4d903 .nl2repo/artifacts/private/sha256/36/36d03a7f2840b4a6cd4d22576dc52f0479aa1b00c6ddef85fd07cc59cba4d903
missing 79d7adb06dd589461714a73ddabe6f8157d70dcded43aa3c89563b2a4b7f3b0d .nl2repo/artifacts/private/sha256/79/79d7adb06dd589461714a73ddabe6f8157d70dcd43aa3c89563b2a4b7f3b0d
missing 883ffff65a1fe5256972090cc49ca607098dddaec0c4b6089f8192d9abb7b679 .nl2repo/artifacts/private/sha256/88/883ffff65a1fe5256972090cc49ca607098dddaec0c4b6089f8192d9abb7b679
```

Commands and results:

```text
uv run nl2repo --help
exit 0; command help displayed

uv run --frozen --project harbor-runner harbor --version
exit 0; Harbor 0.21.0

uv run nl2repo task validate-source catalog/sources/filelock
exit 0; source_digest=sha256:64024a3ae1a5e70bcf9816693b52e372c1f5f5ab8fa20aeacfe92fc89276fd07

find .nl2repo/artifacts -type f -name '<each missing digest>' -print
exit 0; no output for all three digests
```

No compiler, Harbor run, Oracle run, or control run was started. No external
host or source authorization was granted. Existing `catalog/tasks/filelock`
and historical production evidence were not modified.

## Remediation

Register the exact verifier, Oracle, and dependency-lock payloads in the parent
private CAS, then rerun the complete revalidation against the unchanged source
digest. Before accepting any result, compile twice with the locked Python
toolchain and `--allow-private`, require byte-identical bundles, inspect the
Oracle payload for runtime network access, and run Oracle, empty, stub, forgery,
and offline controls. Bind every new compact receipt to the resulting bundle
manifest and retain the failed/skipped leaf sets. Do not authorize GitHub,
codeload, package registries, DNS, or any other external service as a workaround.
