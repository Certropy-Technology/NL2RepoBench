# `go-go-funk` authoring audit: blocked

**Status: blocked.** This source-local record freezes the exact upstream
revision and records why it cannot safely enter the current Go production lane.
No Harbor runtime, private Oracle, controls, or generated `catalog/tasks`
projection is created.

## Frozen source

- Upstream: `https://github.com/thoas/go-funk`
- Revision: `045ef11f8f9f4d83a03adbd0eea420773c6c68bc`
- Git archive SHA-256: `f9885f4e1c771a41afc50dcec82b8df49292cfffc9296bf092538980d10aa922`
- License: MIT
- `LICENSE` SHA-256: `ab1d9bc52e58c23d7be727e33ddb9498014dc273522525b7a5d639483e104845`
- Module path: `github.com/thoas/go-funk`
- Module directive: `go 1.13`
- Source contains 31 root test files and 230 statically discoverable test
  functions/examples/benchmarks.

## Dependency and test probe

The exact checkout was tested with Go `1.26.5-X:nodwarf5` on Linux/amd64 with
`CGO_ENABLED=0`, `GOWORK=off`, `GOPROXY=off`, `GOSUMDB=off`,
`GOTOOLCHAIN=local`, and an empty module/cache directory. It exits before test
collection because `github.com/stretchr/testify@v1.4.0` cannot be resolved when
module lookup is disabled. This is recorded in
`evidence/dependency-probe.log`; it is not an Oracle or verifier receipt.

## API and adapter assessment

go-funk exposes a broad reflection-based utility surface, including collection
operations (`Filter`, `Map`, `FlatMap`, `Flatten`, `Chunk`, `Difference`,
`Intersect`, `Union`, `Without`, `Zip`, `Join`), aggregate/reduction operations
(`Reduce`, `Sum`, `Product`, `Any`, `All`, `Every`), arbitrary function
callbacks (`Find`, `ForEach`, `Filter`, `Map`, `Reduce`, `Join`), reflection
helpers (`IsCollection`, `IsFunction`, `IsPredicate`, `IsType`, `IsZero`),
reflective path mutation (`Set`/`MustSet`), and mutable/lazy builder chains
(`Chain`, `LazyChain`, `Map`, `FlatMap`, `Filter`, `Reduce`, `Values`). It also
contains typed primitive variants and APIs accepting `reflect.Value`.

These signatures accept arbitrary Go types and callback function values. A
JSON-lines bridge cannot preserve the input type identity, function closures,
pointer aliasing, mutation and panic behavior, or `reflect.Value` semantics
without introducing a task-specific RPC protocol. Such a protocol would need
to define a closed type registry, callback language, object identity model,
mutation transactions, and bounded panic/error mapping; none is present in the
upstream contract or approved for this task. Trusted/root tests importing the
candidate directly would violate the separate-verifier boundary.

The task therefore remains blocked pending an approved typed child-side adapter
and a complete private offline module closure. Narrowing the task to a few
primitive helpers would no longer represent this frozen project faithfully.

## Remediation

1. Materialize and hash-lock `testify` and the complete Go module closure.
2. Approve a deterministic child-side protocol for a bounded registry of typed
   values, callback expressions, object identity, mutation, and panic behavior.
3. Freeze public-behavior tests against that protocol, then implement a
   separate verifier and rerun collection, compile, Oracle, and controls.

Until those steps are complete, no production denominator, Oracle reward, or
generated runtime is claimed.
