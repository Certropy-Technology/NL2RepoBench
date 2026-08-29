# `p-locate` Traceability

The frozen upstream suite has 13 AVA leaves plus one tsd file. The private
verifier freezes 38 deterministic `node:test` leaves because it separates
combined upstream behaviors and adds bounded contract/error coverage needed by
the repository-generation task. Every hidden assertion maps to the public
contract below; no assertion names or imports an unexported helper.

| Public contract | Private coverage |
| --- | --- |
| ESM package identity, version, root/default export, declaration, exact runtime dependency, and scripts policy | Package inventory leaf |
| Ordinary arrays, Sets, generators, promised values, objects, empty/no-match behavior | Ordinary iterable leaves |
| Synchronous, asynchronous, and PromiseLike tester results; exactly one resolved argument; strict `true` | Tester/value leaves |
| Input-order default and completion-order opt-out | Two deterministic controlled-race leaves |
| Default, finite, serial, and positive-infinity concurrency; invalid zero/fraction | Seven concurrency/validation leaves |
| Tester throw/rejection, input rejection, iterator failure, and completion/error race | Six error leaves |
| Async iterable values, promised yields, empty/no-match, async tester, strict `true`, and early stop | Seven async leaves |
| Async iterator/tester failures, serial consumption, ignored sync-only options, and async-protocol precedence | Four async boundary leaves |

Callbacks, iterators, promises, and errors are constructed inside a bounded
UID 10001 child. The trusted `node:test` process sends only allowlisted scenario
names and reads bounded JSON responses. The verifier owns collection, network
proof, grading, and reward files.
