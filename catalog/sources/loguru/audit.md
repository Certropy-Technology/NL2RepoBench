# `loguru` Candidate Authoring Blocker

Status: **blocked before source freeze**.

This task-local record deliberately fails closed. The bounded authoring lane did
not obtain enough reproducible evidence to create `task.toml` or a public
behavioral `instruction.md` for `Delgan/loguru`. No commit, license, archive,
test denominator, dependency closure, or verifier boundary is guessed from a
mutable branch, a package release label, an installed distribution, or model
memory.

## Scope and decision

The source authority contains no upstream or hidden test bytes, private
commands, source archive, dependency artifacts, Harbor files, Docker files,
verifier, candidate adapter, Oracle implementation, or shared catalog/dataset
edit. The blocked descriptor and remediation evidence are task-local; the
`catalog/tasks/loguru/` runtime directory remains absent.

The candidate cannot advance past discovery until all evidence below is
collected from one detached, clean checkout and retained with exact commands and
hashes. Publishing a partially inferred record would violate the evidence-first
source, environment, collection, and separate-verifier gates.

## Missing source and license gates

The following required facts were not established in this bounded lane:

- a full 40-hex commit resolved from the intended immutable candidate revision,
  including commit date, subject, tree ID, and submodule state;
- an independently repeatable, unprefixed `git archive --format=tar` SHA-256,
  byte size, and member count for that exact commit;
- SPDX classification corroborated by the exact repository license bytes,
  license file Git blob ID and SHA-256, and package metadata; and
- a source-only LOC count over an explicitly enumerated runtime boundary,
  separating Python implementation from tests, examples, documentation,
  generated files, stubs, and vendored code.

Without those facts, neither a source lock nor a defensible difficulty label can
be written.

## Missing official-test evidence

No official test inventory or source baseline was frozen. A future audit must
identify the exact upstream test roots and configuration, source-declared test
extras, plugin-autoload policy, optional/platform markers, skip/xfail policy,
and all subprocess or shell prerequisites. It must run bounded, cache-disabled
collection repeatedly in the selected interpreter and preserve structured node
IDs and their normalized digest. Static `test_*` definition counts are not a
frozen pytest denominator.

A full baseline, Oracle run, control run, hidden-test adaptation, and Harbor
materialization are explicitly outside this lane and were not attempted.

## Logging, file, serialization, and subprocess risks to resolve

Loguru is stateful logging software, so ordinary function-call serialization is
not enough evidence for a safe task. Before authoring can continue, the exact
revision must be inspected and probed for at least these behavior classes:

- process-global logger/core state, handler IDs, mutation and restoration,
  thread and task interactions, re-entrancy, enqueue queues, and shutdown;
- standard output/error capture, terminal/color detection, exception formatting,
  stack depth, source paths, timestamps, time zones, locale, and environment
  variables;
- path templates, file creation modes, permissions, rotation, retention,
  compression, watching, delayed opening, encoding, newline behavior, symlinks,
  temporary files, and cleanup outside an assigned scratch directory;
- record dictionaries containing exceptions, frames, callables, arbitrary
  `extra` values, custom formatters/filters/sinks, pickling or multiprocessing
  payloads, and serialized JSON/text output; and
- child processes, multiprocessing start methods, queue workers, external
  compression commands, signals, fork behavior, hangs, and platform-specific
  expectations.

All time, PID, thread ID, path, color, traceback, and scheduling observations
need normalization or explicit assertions. Test probes must use temporary paths,
bounded payloads and timeouts, deterministic inputs, and guaranteed logger and
child-process cleanup. No long property or stress test is justified during
candidate authoring.

## Offline-closure gate

No hash-locked offline dependency bundle exists for this task. A reopening
package must distinguish runtime, build, test, optional feature, and tooling
requirements from the exact source metadata and lock files. It must record the
selected Python/OS/base-image digest, resolve marker-selected transitive
artifacts, preserve hashes and licenses, and prove installation, collection,
and the approved test command with network disabled and caches cleared.

A package name/version list is not an offline closure. Optional dependencies
that change collection or logging behavior must be pinned and included, or the
corresponding tests must be explicitly excluded before the denominator is
frozen.

## Separate-verifier and JSON-safe boundary gate

Trusted pytest must not import an untrusted candidate logger. A generic
`{"function": ..., "args": ...}` client is insufficient because Loguru
operations exchange live sinks and callbacks, exception/frame objects,
file-like objects, queue/process state, and persistent handler IDs.

A production task therefore needs a reviewed Loguru-specific child-side
scenario adapter. Trusted requests should be declarative and allowlisted (for
example: configure a built-in sink recipe, emit records, mutate context,
complete or remove handlers, then return normalized observations). Candidate
state and all filesystem effects must stay in the child. Responses must be
strict JSON values with bounded strings/lists/maps and explicit projections for
exceptions and records; they must reject non-finite numbers, arbitrary object
serialization, child-selected paths, imports, commands, and callbacks.
Timeouts, output-size limits, process-group cleanup, and fresh-process isolation
must be part of that contract. No such adapter or private command/test artifact
was available here.

## Reopen conditions

Reopen this candidate only when a task-local follow-up can record:

1. the exact detached revision, repeatable archive digest, license evidence,
   submodule state, and source-only LOC boundary;
2. package/API and official-test inventories tied to that revision;
3. a final immutable environment and hash-locked offline dependency bundle;
4. stable structured collection under an explicit optional/platform policy;
5. bounded source-baseline evidence and a reviewed risk/normalization policy;
6. private test and command artifacts plus a Loguru-specific JSON-safe child
   adapter in the authorized private store; and
7. later, in separately authorized stages, Oracle, negative controls, blind
   review, and publication evidence.

Until then, this audit is a blocker record only and must not be compiled into a
Harbor task or included in a scored dataset.

## Remediation record (2026-08-25)

A bounded descriptor remediation was attempted with Python 3.14.7 and uv
0.12.3. The only retained inventory identity is the historical
`source_tree_sha1` `5262c831f5547977ffbfccfb8f07a05cb1aa9728`; it is not a Git
revision and cannot freeze source bytes. The audit itself hashes to
`sha256:bc318c58a450b1c646aff16603b4ec391faa9d9b5387b8354434dcae168ad96f`
(6,826 bytes). `reports/harbor-production-input-v1.json` records the same
source-tree inventory key but provides no revision, license, archive, lock, or
verifier artifact. The bounded commands `python3 --version` (exit 0),
`uv --version` (exit 0), `sha256sum catalog/sources/loguru/audit.md` (exit 0),
and `test ! -e catalog/tasks/loguru` (exit 0) were run; no source checkout,
Oracle, collection, or control run was claimed. `uv run nl2repo task
validate-source catalog/sources/loguru` exits 0 after descriptor creation and
`uv run nl2repo task lint-network --tasks-root catalog/sources --include-generated`
exits 0 with no loguru error. The task remains **blocked** with failure class
`source`; next step is to resolve and verify a real 40-hex upstream commit,
archive/license hashes, then reopen dependency, collection, verifier, Oracle,
and control gates. The zero-valued revision/digest fields in the descriptor are
schema placeholders only and must never be treated as provenance.
