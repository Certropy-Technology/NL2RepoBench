# Emoji instruction-migration revalidation blocker

- Task: `emoji`
- Expected current catalog source digest: `sha256:17375bfca2cc9e1e9aae9b661519c4711964c5b1e90c18d730489212485c77d2`
- Frozen upstream revision: `d26c675190a6b6c0edee959d7b896721a9c3641d`
- Frozen upstream archive digest: `sha256:0ab5a04e57bc580c66c78743cbfa413612f305bf151755ea72bddf5c9fb919ae`
- Lifecycle: unchanged at `controls-passed`.
- Historical `production-evidence.json`: unchanged.

## Blocker

The parent CAS at `.nl2repo/artifacts`
does not contain any of the four private artifacts required by `task.toml`:

| Artifact | Declared role | CAS status |
| --- | --- | --- |
| `sha256:04d36781723688e76879958d44cefa8957a658970c2abbf1eba7ec3a5c40e117` | Oracle bundle, 4,864,000 bytes | missing |
| `sha256:089efaf118e36d6827593b3ae59897143e2cc618c5c3bd41361fbaa1c46ec29b` | setuptools lock, 99 bytes | missing |
| `sha256:105436531e84163bd64fcb6ceb78ed61f58bd278773dafba35abf5f4c809c395` | separate verifier bundle, 40,960 bytes | missing |
| `sha256:680a0d08619f6dc1440d18048be4ef1c0e471807046cbf3324b798c22cc10e18` | historical evidence record, 2,671 bytes | missing |

The checked paths were:

```text
.nl2repo/artifacts/private/sha256/04/04d36781723688e76879958d44cefa8957a658970c2abbf1eba7ec3a5c40e117
.nl2repo/artifacts/private/sha256/08/089efaf118e36d6827593b3ae59897143e2cc618c5c3bd41361fbaa1c46ec29b
.nl2repo/artifacts/private/sha256/10/105436531e84163bd64fcb6ceb78ed61f58bd278773dafba35abf5f4c809c395
.nl2repo/artifacts/private/sha256/68/680a0d08619f6dc1440d18048be4ef1c0e471807046cbf3324b798c22cc10e18
```

Without the verifier and Oracle bundles, the migrated source cannot be compiled
or tested against its current source digest. No replacement artifact was
fabricated and no network or external host authorization was used.

## Checks completed

These checks were run from the task checkout with runtime network access denied:

```text
uv run nl2repo task validate-source catalog/sources/emoji
  exit 0; source_digest=sha256:17375bfca2cc9e1e9aae9b661519c4711964c5b1e90c18d730489212485c77d2

uv run nl2repo task lint-network --tasks-root catalog/sources
  exit 0; tasks_scanned=480; global_errors=0; emoji_findings=[]

uv run python scripts/validate_instruction_quality.py
  exit 0; instruction quality passed

JSON/TOML parsing and bash -n for the task controls
  passed
```

The four CAS existence checks each returned `missing`. Compilation, Oracle,
empty, stub, forgery, and offline Harbor controls were therefore deliberately
not run. Existing historical receipts were not rebound to the migrated source.

## Remediation

Restore the four exact CAS objects and verify their declared byte sizes and
SHA-256 digests before compiling. Then compile twice with the locked Python
toolchain and `--allow-private`, require byte identity, inspect the Oracle for a
local digest-verified payload, and run the complete Harbor 0.21.0 Oracle,
empty, stub, forgery, and offline matrix under NoNetwork. Persist fresh,
repository-relative, hash-bound summaries before any production evidence or
generated projection is changed.
