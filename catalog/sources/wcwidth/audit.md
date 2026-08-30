# wcwidth authoring audit

The candidate is frozen to commit `551710eabf316ed2d9e3782c1fe9cf80ff0f6ed9` of
`https://github.com/jquast/wcwidth`, with the MIT license and the recorded
`git archive --format=tar` SHA-256 `d8621c78e2a93b9f7a97ee756832a3639e8bbb87c7c79f4c8344ef7fb4bf8fb6`.
The Oracle script re-fetches that exact object, asserts the resolved commit, and verifies the
archive before extracting it. The `ucs-detect` gitlink is recorded as provenance but is not a
runtime dependency.

The package is pure Python, ships generated Unicode tables, and has no third-party runtime
dependency. Hatchling and its complete build closure are hash-locked in
`provenance/requirements.lock.txt`; the candidate install is performed during the image build.
Agent and separate verifier execution are `no-network`, with no static allowed hosts.

The private verifier has 36 fixed JSON scenarios. Candidate code is imported only by the existing
UID-isolated child-side client. The trusted verifier owns collection, JUnit, grading, reward, and
network reports. Scenarios cover codepoint width, grapheme segmentation, ANSI/OSC handling, SGR
state, alignment, wrapping, clipping, terminal profiles, and Kitty/OSC 8 records.

Performance benchmarks, downloaded conformance data, and live terminal probes are excluded because
they are not bounded deterministic API behavior for an offline Harbor task.
