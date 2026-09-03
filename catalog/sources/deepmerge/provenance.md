# `deepmerge` Authoring Provenance

This is a bounded Node/npm task for the frozen upstream revision
`5b87756a5671635679001cbac72aa42f23472c81`.

## Source Freeze

- Upstream: `https://github.com/TehShrike/deepmerge`
- Commit: `5b87756a5671635679001cbac72aa42f23472c81`
- Commit tree: `2331f2255f4c8de659e878b778b8ddd47e8db850`
- Commit subject: `4.3.1`
- Raw `git archive --format=tar` SHA-256: `sha256:6efceb65f541465fe6755f427fd8ca33f925b36a56b38f39ab1282bf9830b51d`
- License: MIT, from `license.txt`; the license bytes are hash-recorded in the task evidence.

The upstream repository contains a v2 npm lock with development, test, build,
and git-based packages. It does not declare a runtime dependency even though
the source entry imports `is-mergeable-object`; the published package is made
from the Rollup build and inlines that helper. The production task therefore
uses a scripts-free, zero-runtime-dependency publication adaptation with the
same observed helper semantics.

## Scope And Adaptation

The full upstream suites use Tape callbacks, symbols, Dates, regular
expressions, class instances, and TypeScript/build tooling. The fixed contract
uses 32 deterministic JSON-boundary leaves, while constructing those special
fixtures locally in the candidate child when needed. It is a behavior slice,
not a claim of complete JavaScript-value or build-tool parity.

Private Oracle, tests, command plan, and dependency bytes are content-addressed
under `.nl2repo/artifacts` and are never copied into the Agent image.
