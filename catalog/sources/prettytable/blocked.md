# prettytable candidate audit

Status: `blocked`

This evidence-first candidate targets `prettytable/prettytable` at the
requested immutable revision. It is audit-only, not a publishable task, Harbor
bundle, or legacy projection.

## Candidate

| Field | Value | Evidence |
| --- | --- | --- |
| task id | `prettytable` | requested |
| upstream | `prettytable/prettytable` | requested; URL not independently frozen |
| revision | `3c80d392d32f48b0ab1e368793ddb751dbe41807` | requested; full SHA shape |
| language | Python | requested |
| package manager | pip/uv | not frozen |

## Gate results

All gates remain `missing`; no pass is inferred from package metadata or an
unexecuted probe.

| Gate | Evidence required before authoring |
| --- | --- |
| Exact source/archive | Clean exact-SHA checkout, archive bytes, tree listing, and repeatable archive SHA-256 |
| License | Frozen license bytes, SPDX identification, and redistribution decision |
| Source-only LOC | Reproducible implementation-only count plus included/excluded file manifest |
| pytest/golden tests | Clean collection, stable leaf IDs, full upstream result, and golden fixture inventory/hashes |
| pure-Python `wcwidth` closure | Hash-locked offline dependency closure and import probe showing no native extension |
| text boundary | Repeatable byte-identical probes for alignment, Unicode width, empty/multiline cells |
| HTML boundary | Repeatable byte-identical probes for escaping, headers, and empty tables |
| JSON boundary | Repeatable byte-identical probes for field order, Unicode/scalars, and empty tables |
| `tabulate` overlap | Public API/behavior inventory, duplicate review, and a written distinctness decision |

The requested commit does not by itself prove any of the archive, license,
LOC, test-denominator, dependency, determinism, or overlap claims.

## Unblock evidence

Run against a clean, network-isolated source copy and retain versions, exit
codes, stdout/stderr, file lists, hashes, and timestamps in the audit store:

```text
git fetch --no-tags <upstream-url> <revision>
git archive --format=tar --output=prettytable-3c80d392.tar <revision>
sha256sum prettytable-3c80d392.tar
git ls-tree -r --full-tree --name-only <revision>
cloc --by-file --include-ext=py <frozen-tree>
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest --collect-only -q <tests>
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q <tests>
uv lock --offline
uv sync --frozen --offline
python -c 'import wcwidth; print(wcwidth.__file__)'
# Run fixed text/HTML/JSON fixtures twice in fresh processes and compare bytes;
# run a separate public-symbol comparison against tabulate.
```

## Scope decision

No `task.toml`, public `instruction.md`, hidden tests, Harbor/private assets,
dependency cache, or shared index was created. This candidate must stay
blocked until every gate has recorded evidence; after that, add only a minimal
task-local metadata/spec pair and rerun the publication checks.
