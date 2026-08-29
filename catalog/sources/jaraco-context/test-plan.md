# Test Plan

## Upstream Collection

The frozen source contains `tests/test_safety.py` with one parametrized test and
five collected nodes under CPython 3.12.11 with `pytest==9.0.2` and
`portend==3.2.1`. The Python 3.12.11 probe collected five nodes and executed
four: the `subdir/../` case is skipped by the upstream version guard because
the source explicitly documents a Python 3.12 extraction limitation.

## Production Denominator

The production verifier freezes 43 unique `custom-json-v1` leaves. They cover
metadata and exports, context-manager cleanup, composition order, exception
capture and decorators, suppression and interrupt policy, tar filtering and
traversal, streamed tarball behavior, repository command construction, and the
read-only removal callback. Five upstream safety paths are retained as direct
private leaves, while network service behavior is adapted to an in-memory tar
stream and a mocked subprocess command list.

Collection is valid only when the private runner returns exactly 43 unique leaf
IDs, every leaf is `passed`, `failed`, or `skipped`, and the generated collection
and JUnit reports contain the same denominator. The metric is
`clamp(passed / frozen_total, 0, 1)`.
