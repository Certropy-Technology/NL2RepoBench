# `dateparser` Evidence-First Candidate Audit — Blocked

**Status: blocked at discovery/source-freeze gates.**

This is a task-local blocked audit record paired with a parseable declarative
descriptor. The bounded lane did not establish the immutable upstream evidence
required to create a runtime task or an implementable public instruction. It
therefore fails closed rather than turning a likely repository name, mutable
branch, package release, installed wheel, or model recollection into a source
lock.

## Scope

The source authority contains no copied upstream source, license bytes,
official or hidden tests, dependency artifacts, source archives, Harbor/Docker
assets, candidate adapter, Oracle, controls, generated manifest, or legacy
projection. The blocked descriptor and hashed remediation evidence are the only
durable additions; `catalog/tasks/dateparser/` remains absent.

The repository name `scrapinghub/dateparser` is only the user-supplied likely
lead in this lane. Its authority for the `dateparser` distribution, redirect or
organization history, and an exact full Git revision were not independently
resolved before the bounded evidence window closed. No URL or commit is
therefore promoted to canonical metadata.

## Gate audit

| Gate | Result | Evidence required to reopen |
| --- | --- | --- |
| Authoritative upstream | **blocked** | Correlate the package index project links and exact source metadata with the Git remote and repository package metadata; record redirects without substituting a mirror or fork. |
| Immutable revision | **blocked** | Resolve and detach one full 40-hex commit; record commit/author dates, subject, parent(s), tree ID, clean status, tracked-file count, and submodule state. |
| License and archive | **blocked** | Hash the exact revision's license bytes and Git blob, corroborate its SPDX expression with package metadata, and compare at least three independently generated unprefixed `git archive --format=tar` outputs by SHA-256, size, and member count. |
| Source-only size | **blocked** | Enumerate the runtime Python boundary first, including generated/bundled locale data policy, then report physical and nonblank/non-comment LOC separately from tests, docs, examples, scripts, stubs, fixtures, and vendored/generated files. |
| Official tests | **blocked** | Identify upstream pytest roots/configuration and exact test dependency groups, then preserve cache-disabled structured collection and normalized node-ID digests from repeated runs in the selected final interpreter. Static `test_*` counts are not a denominator. |
| Locale/time-zone closure | **blocked** | Inventory package data and all runtime/build/test/optional dependencies from the exact revision; prove locale and time-zone data provenance and include every selected artifact in a hash-locked offline bundle. |
| Determinism | **blocked** | Define and probe a fixed clock, relative base, locale/language order, `TZ`, time-zone database, Unicode/regex behavior, environment, and platform policy with bounded repeated cases. |
| Offline feasibility | **blocked** | Pin OS, Python, base image digest, build backend, wheels/sdists, hashes, markers, and package-data files; replay build, install, import, collection, and approved tests with networking disabled and caches cleared. |
| Separate verifier / JSON | **blocked** | Review and implement a dateparser-specific child protocol whose requests and observations are strictly bounded JSON; trusted pytest must not import candidate code. |

Because every publication-critical gate above is unresolved, this record does
not declare a version, difficulty, category, test count, environment, source
lock, dependency bundle, or lifecycle state in `task.toml`.

## Source, archive, license, and LOC evidence plan

A follow-up must work from one clean temporary clone and retain exact command
transcripts. It must distinguish the canonical repository from similarly named
packages, mirrors, forks, documentation sites, and registry artifacts. A tag or
release label is not an immutable revision until resolved to and recorded as a
full commit.

Archive reproducibility must use the same unprefixed tree archive operation on
the detached revision. Hashing a GitHub-generated source tarball alone is
insufficient because generated tarball bytes can vary independently of the Git
tree. License review must bind the repository license blob and bytes to the
same revision and check any separately licensed bundled language/time-zone data.

The LOC boundary must be explicit before counting. In particular, data files or
generated Python modules that encode language/date knowledge must not be
silently counted as handwritten implementation or silently excluded from the
artifact inventory. Both their source/provenance and their presence in the
installed distribution matter even when they do not contribute Python LOC.

## Official-test and dependency evidence plan

No official test was executed or collected in this lane. A reopening audit must
inspect the exact revision's build metadata, lock files, pytest configuration,
CI matrix, fixtures, package-data declarations, and test extras before choosing
commands. It must record at least:

- Python versions and OSes exercised upstream, plus the one proposed benchmark
  environment;
- test roots, plugin autoload policy, marker/addopts behavior, parametrization,
  skip/xfail policy, and optional suites;
- subprocesses, shell tools, network or downloaded-data assumptions, locale
  availability, filesystem fixtures, and environment mutation;
- runtime, build, test, optional, documentation, and tooling dependencies as
  distinct sets, with marker-selected transitive artifacts; and
- repeated `--collect-only` results as structured node IDs, collection exit
  status, count, and normalized digest.

Names commonly associated with date parsing, regular expressions, locale
selection, local time-zone discovery, IANA time-zone data, or date arithmetic
must be derived from this exact revision rather than assumed. The audit must
also determine whether locale resources are repository package data, generated
outputs, an external distribution, operating-system data, or a combination.
A warm host cache or a successful ordinary install is not offline-closure
evidence.

## Locale, time-zone, and determinism risks

Date parsing is environment-sensitive. Before a denominator can be frozen, a
bounded probe matrix must explicitly control or normalize:

- current date/time and every relative-date base;
- process `TZ`, local-zone discovery, daylight-saving transitions, ambiguous
  and nonexistent wall times, UTC offsets, abbreviations, and the exact IANA
  database source/version;
- requested languages/locales, language detection and ordering, region,
  normalization, Unicode version, month/day naming, and locale resource order;
- settings that prefer dates, months, locale order, first day of week, future
  or past dates, strictness, incomplete dates, and output time zones;
- platform, Python version, hash/random seeds, regex engine/version, filesystem
  encoding, and environment variables; and
- callbacks or custom language-detection functions, warning/error behavior,
  malformed inputs, very long inputs, and denial-of-service bounds.

Time-dependent tests must receive an explicit fixed relative base or a reviewed
clock operation; merely running them quickly is not determinism. Time-zone
observations must preserve enough structure to distinguish equal wall-clock
text with different offsets or folds. Locale auto-detection must not depend on
unordered ambient data. Repeated probes should use small curated inputs and
hard time/output limits; broad fuzzing, stress tests, or full baselines are
outside this candidate-authoring lane.

## JSON-safe candidate boundary assessment

The generic function client is not sufficient without adaptation. Date parsing
can return Python `datetime` values and richer result/search objects, while
settings may include datetime values and some APIs may accept callbacks. Those
objects are not plain JSON, and a fresh generic call does not by itself define
clock, locale, time-zone, or state semantics.

A feasible **proposal for later review**, not a frozen scored contract, is one
allowlisted child-side scenario per isolated process:

1. The request selects an inventoried operation such as parse, date-data, or
   search only after its exact revision-specific signature is confirmed.
2. Inputs are bounded UTF-8 strings, arrays of language/locale strings, region,
   date-format strings, and an allowlist of settings containing JSON scalars or
   lists. Relative bases use an explicit tagged datetime object. Arbitrary
   imports, callables, detector callbacks, object pickles, commands, paths,
   network locations, and non-finite numbers are rejected.
3. The child fixes the approved environment and constructs any datetime or
   settings objects internally. A scenario may retain state only for its own
   bounded operation sequence; no handle crosses processes.
4. Results project to strict JSON: parse success/null; matched text; numeric
   date/time fields; ISO text; offset seconds; zone name/key where defined;
   fold; precision/period; detected locale/language; and normalized exception
   type/message. The exact fields must be derived from the retained upstream
   assertions. Datetime equality must not be reduced to a lossy display string.
5. Requests, responses, recursion, strings, matches, runtime, memory, and output
   are bounded. Each child runs in its own scratch directory with no network,
   has process-group cleanup, and cannot write trusted collection, JUnit,
   grading, or reward artifacts.

This shape can plausibly cover a reviewed JSON-facing subset, but it does not
prove full upstream-test parity. Tests that monkeypatch candidate internals,
pass live callbacks/classes, rely on in-process identity, or inspect unsupported
rich objects need faithful child-side scenario operations or must remain out of
a newly reviewed contract. They may not be dropped silently while claiming the
complete upstream suite.

## Blockers and reopen conditions

Keep this candidate out of compilation and scored datasets. Reopen only when a
task-local follow-up can provide all of the following without adding private
bytes here:

1. authoritative upstream resolution and one exact detached full commit;
2. reproducible archive, license/blob, package-data, submodule, and source-only
   LOC evidence tied to that commit;
3. static API/package/test inventory and repeated structured official-test
   collection in a selected immutable environment;
4. an explicit locale, clock, language-detection, time-zone database, DST, and
   normalization policy supported by bounded deterministic probes;
5. a complete content-addressed no-network dependency and data closure;
6. a reviewed dateparser-specific JSON child contract plus private test and
   command artifacts in the authorized private store; and
7. later, under separately authorized stages, source baselines, Oracle runs,
   negative controls, blind/traceability review, and publication approval.

Until those conditions are met, do not create `task.toml`, `instruction.md`, a
Harbor tree, hidden tests, verifier assets, or an Oracle from this audit.

## Validation record

This lane performed repository-guidance and nearby candidate-record inspection
only. It did not claim upstream network evidence, run dateparser code or tests,
materialize external artifacts, invoke Docker/Harbor, or stage files. The sole
output is this fail-closed audit record.
