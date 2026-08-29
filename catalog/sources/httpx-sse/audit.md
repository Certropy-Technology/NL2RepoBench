# Authoring Audit

## Scope

This `author-one` lane freezes `httpx-sse` 0.4.3 at commit
`ccba32e3f9b03d1c1c42b788fdae7ea59ebcb9b8`. The source archive was refetched
and reproduced byte-for-byte. Its SHA-256 is
`b8c8d892b6c6557f7ffebf2dd28a14b2d4b12b30ff2c6f110736e7f5ff852220`.

The task exposes the package's synchronous and asynchronous SSE model, parser,
event source, context-manager helpers, exports, errors, and deterministic HTTPX
request behavior. Live servers and reconnection policy are outside the scored
contract.

## Baseline And Verifier

The frozen upstream source passed 59/59 tests on CPython 3.12.11. The production
verifier is a separate `custom-json-v1` process boundary with 26 fixed leaves.
Candidate behavior runs as UID 10001 using only JSON-safe values. Each child is
bounded to two seconds, while the trusted verifier owns collection, JUnit,
grading, network, and reward artifacts.

The dependency lock is hash-locked and installed during Docker build. Candidate
installation uses `pip --no-deps --no-build-isolation` into candidate-owned
storage. Agent and verifier execution are no-network; agent allowed hosts remain
empty.

## Final Matrix

| Run | Valid | Passed / collected | Reward | Network |
| --- | --- | ---: | ---: | --- |
| Oracle | true | 26 / 26 | 1.0 | false |
| Empty | true | 0 / 0 | 0.0 | false |
| Stub | true | 0 / 26 | 0.0 | false |
| Forgery | true | 0 / 26 | 0.0 | false |
| Install hang | true | 0 / 0 | 0.0 | false |
| Call hang | true | 0 / 26 | 0.0 | false |
| Offline Oracle | true | 26 / 26 | 1.0 | false |

Empty and install-hang use the permitted `candidate-installation-failed`
exception. The install-hang candidate was terminated with trusted outcome
`timeout`. Forgery wrote candidate-owned reward/grading files, but the trusted
grading remained byte-identical to stub at 0/26.

## Handoff Boundary

The task is `controls-passed`, not reviewed, piloted, or published. This lane did
not start a Harbor model Agent Run and did not generate
`catalog/tasks/httpx-sse/`. The shared toolchain's declared agent runtime image
ID is not present locally; the integrator must restore and verify that immutable
image before the future model run.
