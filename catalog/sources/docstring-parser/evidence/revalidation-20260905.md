# Instruction Revalidation Remediation

Status: **pending artifact restoration**. This record covers the revalidation
after the instruction migration for the frozen source revision. It does not
change the task lifecycle or replace historical production evidence.

## Source identity

- Task: `docstring-parser`
- Catalog source digest validated by `nl2repo task validate-source`:
  `sha256:fcdc966dc2926a20f156502a43c2b088035adc0f1d9f1b54a4b128038e5c888c`
- Existing lifecycle: `oracle-passed`
- Existing frozen source archive digest:
  `sha256:2cb59707c20099e0f8b61ab9eeb6faeb7fea370a03b3468c822f84c0ac21f3e9`
- Runtime policy: no network for agent, candidate, verifier, Oracle, and
  controls; no source-host, registry, DNS, or service authorization.

## Offline artifact precheck

The parent CAS was checked without network access. Each expected object was
absent at its repository-relative content-addressed location under
`.nl2repo/artifacts/private/sha256/<prefix>/`. The expected object sizes and
roles are recorded below; no substitute artifact was accepted.

| Digest | Expected bytes | Role | Result |
| --- | ---: | --- | --- |
| `sha256:88481b4202fa7481ee4a1257646c170f986aeacb2fa6fee91284dba036e6ca40` | 1035 | lifecycle evidence JSON referenced by `task.toml` | missing |
| `sha256:c3761d51e1ef6be43bca30617d589d428b33f8025473de20f01282f5ece2d6b9` | 520 | hash-locked verifier/build dependency lock | missing |
| `sha256:d5ecf42a87e0a3744533459a1f3fba37e9731851dfdedccefeb0ac00b9a6d855` | 235520 | private Oracle bundle | missing |
| `sha256:df387818cbee7d7f9558b80af8a6b974ba3180a2728ea3354bf0a59a7f8a71cd` | 20480 | private separate-verifier bundle | missing |

Because the dependency lock, verifier bundle, Oracle bundle, and referenced
lifecycle evidence are unavailable, this lane cannot produce a durable new
compile or Harbor receipt. This is an artifact/verifier revalidation blocker,
not evidence that the task is unsupported.

## Checks completed

- `uv run nl2repo --help`: passed; current CLI loaded successfully.
- `uv run nl2repo task validate-source catalog/sources/docstring-parser`:
  passed; digest and existing `oracle-passed` status matched the expected
  source contract.
- `uv run python scripts/validate_instruction_quality.py`: passed.
- Full source-root network lint, filtered to `docstring-parser`: passed with
  zero task-specific findings. Unrelated catalog warnings were not attributed
  to this task.
- JSON/TOML and existing shell controls were inspected offline; no source-local
  files were modified other than this remediation record.
- Compile, Oracle, empty, stub, forgery, and offline Harbor runs: **not run**
  because the required CAS objects are missing.

## Remediation

Restore all four exact CAS objects after verifying their bytes and sizes. Then
revalidate the source digest, compile the source twice with the locked Python
toolchain, inspect the resulting Oracle payload for runtime network access, and
run a fresh Harbor 0.21.0 Oracle plus empty, stub, forgery, and offline controls.
Persist compact collection, grading, network, result, failure-set, and bundle
manifest summaries in this directory before any production evidence update.
