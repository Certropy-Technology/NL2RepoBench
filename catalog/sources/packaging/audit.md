# `packaging` Candidate Authoring Audit

Status: **blocked at source freeze**.

This task-local audit intentionally contains no `task.toml` or
`instruction.md`. The bounded evidence window ended before an immutable
upstream revision was established, so creating either file would require
inventing source, version, test, or API facts. No upstream source bytes,
official tests, hidden assertions, dependency artifacts, Harbor assets,
verifier, or Oracle material are included.

## Scope and decision

The requested candidate is the Python project `pypa/packaging`. The checkout
had no existing `catalog/tasks/packaging/` authoring record when this lane
started. Repository authoring policy requires an exact full commit, auditable
license evidence, deterministic source archive digest, source-only LOC,
official-test provenance and collection evidence, package metadata/version,
behavioral API inventory, an offline dependency closure, and a reviewed
candidate subprocess boundary before a task can advance.

Those facts were not available in the inherited context and were not resolved
before the run's bounded inspection limit was reached. Consequently:

- no branch, tag, PyPI version, or current default-branch head is presented as
  an immutable source revision;
- no SPDX identifier, archive digest, LOC value, version, API count, official
  test count, or dependency list is guessed;
- no collection count is presented as a frozen denominator;
- no direct trusted-process import of candidate code is proposed as a
  substitute for the required separate-verifier boundary; and
- no task lifecycle claim beyond this discovery blocker is made.

This is an authoring/infrastructure blocker, not evidence that the upstream
project fails a size, license, test, or quality gate.

## Evidence acquired in this lane

The repository-level authoring contract was checked against the current
catalog patterns before stopping:

1. `catalog/tasks/<task-id>/task.toml` and `instruction.md` are the only
   human-authored task source when enough evidence exists.
2. Unknown provenance must remain unknown; it must not be inferred from a
   README, mutable URL, package name, or legacy projection.
3. A source-only candidate may remain blocked when immutable environment,
   offline closure, private tests, command artifacts, and a subprocess adapter
   are absent.
4. Hidden tests, private bytes, Harbor trees, and Oracle runs are outside this
   task-local lane.

No source checkout, package installation, official test execution, long
property probe, network credential, Docker operation, or shared catalog edit
was performed.

## Required evidence to reopen

A follow-up authoring lane should perform only bounded, retained probes and
record their exact commands and outputs:

1. Resolve an owner-approved release/ref to a full 40-character commit, detach
   at it, record commit/tree/time, submodules, and a clean status.
2. Hash two independent unprefixed `git archive --format=tar <commit>` streams;
   record byte/member counts and verify the digests agree.
3. Hash and classify the license file and cross-check repository and built
   distribution metadata without copying license bytes into the catalog.
4. Parse the exact revision's build metadata to establish distribution/import
   names, version mechanism, Python range, build backend, runtime dependencies,
   extras, package data, and entry points.
5. Count tracked implementation files separately from tests, docs, examples,
   generated files, vendored code, stubs, and benchmarks; record physical,
   nonblank, and noncomment source-only LOC and apply the approved difficulty
   policy.
6. Inventory exports, public classes/functions/methods/properties/constants,
   signatures, aliases, exceptions, metadata/version APIs, tags/versions,
   markers/specifiers/requirements behavior, and serialization/error seams.
   Map official tests to those public behaviors before drafting a specification.
7. Identify the upstream-maintained functional test set and run bounded,
   cache-disabled collect-only checks in an explicit Python/pytest/plugin
   environment. Preserve item identities and collection errors; do not call a
   provisional count a frozen denominator.
8. Resolve and hash-lock build and selected test dependencies into a
   distributable offline artifact, then replay build/import/collection with
   networking disabled. A warm local cache is not a dependency bundle.
9. Design a task-specific child protocol for rich `packaging` objects and
   exceptions. Trusted tests must receive JSON-safe observations from an
   untrusted candidate subprocess rather than import candidate modules.
10. Only after those facts are reviewed, add `task.toml` and an implementable
    behavior-first `instruction.md`. Private tests, Harbor assets, Oracle, and
    controls remain separate authorized stages.

Until that evidence exists, the safe result is this explicit blocker rather
than a fabricated candidate.
