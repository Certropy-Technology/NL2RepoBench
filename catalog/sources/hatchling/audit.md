# Hatchling authoring audit

This task was authored from a detached checkout and fixed upstream commit. The
worker wrote only `catalog/sources/hatchling/`, task-local private content under
`.nl2repo/`, and the required handoff. No Harbor model Agent Run was started.

## Source commands

```text
git ls-remote https://github.com/pypa/hatch.git HEAD
git clone --filter=blob:none https://github.com/pypa/hatch.git <task-local-source>
git checkout --detach ed8e30bebf98f2fe4d70c18a32a50a8160c391cb
git archive --format=tar HEAD | sha256sum
git archive --format=tar HEAD backend | sha256sum
sha256sum backend/LICENSE.txt
```

The remote, detached checkout, and declared revision matched. Both full and
backend archive streams were generated directly by Git. The backend archive is
the task source digest; the full archive digest corroborates repository
authority.

## Reference observation generation

The exact backend subtree was installed to a task-local target with no runtime
dependency resolution after installing the 7-package hash lock. The 21
candidate-side scenarios were executed with Python `-I -B`; every report had
`schema_version=1.0`, `ok=true`, the expected scenario ID, and JSON-safe output.
Those observations were frozen as `expected.json`. The scenario sources and
expected bytes are private artifacts and are not present in the public source
catalog.

One initial `version-file` probe exposed an upstream semantic detail: the
default `VersionFile.write()` template uses a dual assignment while the default
read regex recognizes a single assignment. The final contract therefore tests
`read/set_version` on the documented single-assignment form and tests `write`
as an independent output operation. No implementation behavior was hidden or
changed to force the two operations to round-trip.

## Storage remediation

The shared project volume reached capacity twice. First, the task-local
reference installation and observation outputs were removed after expected
values were frozen. Second, an unintended task-local `.venv` partially created
by `uv run` was removed, and the existing repository environment was used to
ingest private artifacts. These were infrastructure/storage events, not source,
candidate, or verifier failures. No parent or sibling lane data was deleted.
