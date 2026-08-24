# Remediation Inventory

## Source freeze

- Upstream: `https://github.com/lidatong/dataclasses-json.git`
- Revision: `dc63902eeb5e1c5ce1ea4e078c50e0eb9bc1a541`
- Commit: `dc63902 Warn about buggy type resolution (#529)`
- Commit timestamp: `2024-06-09T08:20:35-06:00`
- License: MIT (`LICENSE`, SHA-256 `52321b55695e8919b7c654b1e8083c57cf212b885f42871bd6c3cdd2dd267f0f`)
- Reproducible git archive digest: `sha256:113c90da5957f13cc49f80d535cde965e66850f72559498a9ebfd934c4db449f`
- Source tree: 39 Python files, 5,142 Python LOC, 30 upstream test modules.

## Baseline diagnosis

The frozen source was executed with Python 3.10 and its locked development
dependencies. Command:

```text
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest --continue-on-collection-errors tests --junitxml=/tmp/dcj-baseline-junit.xml
```

Observed result: **325 passed, 3 skipped**, exit code 0, 1.08 seconds, 207
warnings. This is diagnostic evidence only, not this task's denominator. The
full upstream surface contains dynamic schema, union, generic, callback,
Marshmallow and type-resolution behavior that is not suitable for a compact
JSON-safe subprocess contract.

## Selected contract

The 24 verifier cases cover root exports, decorator/mixin methods, primitive
and nested dataclass round trips, containers, enum and optional values, JSON
options, field naming/exclusion, custom encoder/decoder metadata, schema dump
and load, and all three unknown-field policies. They are newly authored from
the public behavior above; the upstream tests are not copied into the task.

## Runtime/build selection

- Diagnosis runtime: CPython 3.10.
- Pinned Harbor runtime: CPython 3.12 slim,
  `python@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a`.
  The frozen project declares Python `>=3.7,<4.0`, so this is compatible.
- Build backend: `poetry-dynamic-versioning==1.8.2` with
  `poetry-core==1.9.0`, `dunamai==1.23.0`, `jinja2==3.1.6`,
  `markupsafe==2.1.5`, and `tomlkit==0.12.5`.
- Candidate build result: `dataclasses_json-0.0.0.post1.dev0+dc63902-py3-none-any.whl`,
  SHA-256 `ced45e3ee7df4085c28875763a8ce20ab788bdef560e086e8d08d0da73e3d2ea`.

The initial Poetry installation attempt failed because its installer selected a
nonexistent system site-packages target. Poetry export plus hash-checked pip
installation then succeeded. The backend initially failed due to missing
`poetry_dynamic_versioning`, then due to missing Jinja2/MarkupSafe; all were
installed pinned and the build succeeded. Full command and exit evidence is in
`provenance/commands.log`.
