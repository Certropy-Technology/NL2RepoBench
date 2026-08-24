# `jsonschema` Static Authoring Audit

**Status: blocked.** This directory is an evidence record only. It contains no
public task instruction, `task.toml`, Harbor bundle, Docker asset, Oracle
solution, hidden/private test bytes, dependency cache, verifier, or shared
catalog/index update. The block is a source-freeze blocker, not a model or
runtime test result.

## Authoritative candidate record

The only approved candidate source for this audit is
`reports/python-package-candidates.v1.md` (and its machine-readable companion
`reports/python-package-candidates.v1.json`). Their current SHA-256 values are:

```text
reports/python-package-candidates.v1.md   8b69e9658705324979bd6b540c114a2f488488dfad34298c10530b23b6f9a2c5
reports/python-package-candidates.v1.json  fd613b5114ac315e3d3276ef10c7dbf8dab1b3e0d899d8be4f1c2009302c2bc4
```

The Markdown shortlist records only the following discovery metadata:

- package/distribution: `jsonschema`;
- repository: `https://github.com/python-jsonschema/jsonschema`;
- category: validation;
- discovery stars: 4,972;
- reported license: MIT;
- reported Python share: 100%;
- reported last push: 2026-08-17;
- status: candidate, with the note **test layout audit pending**.

The JSON shortlist contains the same record and gives the reason
`root test layout needs explicit collection audit`. The report's
`deep_validation` array contains ten other packages, but does **not** contain a
`jsonschema` entry. Consequently it supplies no `revision`, commit date,
tree, source SLOC, API estimate, test-file count, static test-definition
count, runtime-dependency count, offline-risk list, or recommendation for this
candidate.

Most importantly, neither authoritative report field lists a commit SHA for
`jsonschema`. A branch, tag, `latest` checkout, package release, or commit
found outside the report is not an approved substitute for the exact revision
required by this task. No source checkout was therefore selected or inspected.

## Source and license audit

The discovery row is useful eligibility evidence, but it is not a source lock.
The reported `MIT` value cannot be promoted to frozen license evidence without
an exact revision. The following required facts remain unavailable:

- full immutable commit and its reachability from the named repository;
- deterministic source archive/tree digest and submodule state;
- exact `LICENSE` path, bytes, copyright scope, and SPDX evidence at that
  commit;
- package metadata and build files at that commit; and
- any source/package overlay that a future verifier image might apply.

No claim is made here that the current upstream default branch, a PyPI
release, or an unpinned source archive matches the candidate intended by the
report. Until the report supplies a full revision, source and license status
must remain `unknown`/blocked rather than guessed from discovery metadata.

## Test layout and collection audit

The report explicitly marks the root test layout as pending review. Because no
revision is authorized, this lane cannot determine:

- whether tests live at `tests/`, a root-level pattern, or another path;
- pytest configuration, collection hooks, plugins, fixtures, or generated
  cases;
- whether tests require files outside the package tree;
- parametrization, skips, xfails, doctests, or collection-time imports;
- the effective node IDs and frozen denominator; or
- whether the report's eventual test command can run in a clean offline
  environment.

No `pytest --collect-only`, test execution, Docker/Harbor run, or collection
artifact was performed. There is no defensible `expected_total`; the report's
shortlist has no test count for this candidate, and a guessed static count
would not satisfy the fixed-collection contract.

## Runtime and development dependencies

No approved revision means no `pyproject.toml`, `setup.py`, `setup.cfg`,
requirements file, lockfile, build backend declaration, optional-extra list,
or test configuration was inspected. Runtime and development dependency sets
are therefore **unknown**. In particular, this audit does not infer that the
package is dependency-free merely because it is Python-dominant, and it does
not treat a PyPI metadata response or an unpinned lock generated from another
revision as a frozen offline closure.

Before packaging, a future lane must identify and separately review:

1. runtime dependencies and their transitive closure;
2. build-system requirements and build isolation behavior;
3. test/development dependencies and pytest/plugin versions;
4. Python, OS, and architecture constraints; and
5. a content-addressed, hash-checked offline dependency bundle.

No wheel, sdist, lockfile, registry response, cache, or dependency bytes were
copied into this task directory.

## JSON-safe API scope

An API inventory cannot be performed against an unspecified revision. This
record therefore defines **no scored API scope** and makes no claim that the
whole `jsonschema` package, or any subset of it, can cross the generic JSON
candidate boundary.

A future authoring lane must inspect the exact source and decide explicitly
which behavior is representable by a child-side JSON request/response adapter.
The decision must cover, based on observed APIs rather than package-name
assumptions:

- schema and instance value domains and their JSON encodings;
- format/checker and resolver/registry customization;
- callback, extension, error, and exception behavior;
- state retained across calls and process boundaries;
- ordering, URI/reference resolution, filesystem or network access; and
- non-JSON Python values, if any, and their approved tagged representation.

Trusted verifier tests must not directly import candidate code merely to avoid
this inventory. If upstream behavior requires Python objects, callbacks,
mutable state, or process-local registries, a task-specific child adapter is
required; unsupported behavior must be narrowed in a reviewed instruction and
metric contract rather than silently omitted.

## Separate-verifier feasibility

Separate-verifier feasibility is **not assessed** because the source revision,
test inventory, and public API contract are all missing. No candidate client,
subprocess protocol, private command plan, hidden test reference, grader, or
artifact resolver was created. The generic policy remains applicable:

- candidate implementation runs outside trusted grader imports;
- requests and observations crossing the boundary are JSON-safe and
  schema-checked;
- hidden tests and expected values remain private;
- verifier collection and scoring are structured and independently written;
- network is disabled by default; and
- forged candidate-side reward or test files cannot affect grading.

A future feasibility review must map every retained assertion to an adapter
operation and every public behavior to at least one test. It must also record
which upstream tests are intentionally out of scope, if any, and why that is a
new reviewed task contract rather than an unannounced parity claim.

## Reopen conditions

Reopen this candidate only after the authoritative candidate report (or an
approved revision of that report) supplies a complete immutable commit SHA.
Then, in a new static-authoring lane:

1. detach a clean checkout at exactly that SHA and record source/archive,
   submodule, package-layout, and license hashes;
2. inventory public APIs, CLI/entry points, fixtures, test paths, and all
   runtime/build/development dependencies;
3. run collection in the final pinned environment and preserve structured
   node IDs, skip/xfail policy, collection errors, and a fixed denominator;
4. design and review a JSON-safe child adapter for the actually retained API
   surface, without direct trusted imports of candidate code;
5. provision private test/command/Oracle references and a complete offline
   dependency closure outside this public task directory; and
6. only in a later execution phase run the three Oracle gates and the empty,
   stub, forgery, and offline controls.

Until those conditions are met, do not create `task.toml` or `instruction.md`,
add the task to a dataset, infer a denominator, or describe `jsonschema` as
frozen, packaged, Oracle-passed, or publishable.

## Static validation performed

This lane performed only local, non-executing evidence checks:

- read `AGENTS.md`, the task-authoring/metadata guidance, and the candidate
  report;
- parsed and inspected the report's JSON candidate records and confirmed
  that `jsonschema` is present only in `shortlist`, not `deep_validation`;
- verified that neither the legacy task tree nor the catalog already contains
  a `jsonschema` task entry; and
- computed the report hashes recorded above.

Not performed by policy: upstream checkout or network retrieval, Docker,
Harbor, dependency installation, pytest collection/execution, hidden-test or
Oracle materialization, private artifact access, and shared-catalog edits.
