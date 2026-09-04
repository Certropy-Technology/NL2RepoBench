# `go-go-mysql` Go authoring audit: blocked

**Status: blocked.** This is a source-local audit, not a published Harbor task.
No `catalog/tasks/go-go-mysql/` runtime, private test bundle, Oracle bundle,
module cache, credentials, or shared-index change is created by this lane.

## Frozen source

- Upstream: `https://github.com/go-mysql-org/go-mysql`
- Exact revision: `9ed3a7186e2b591989d8af214de2120e7a26008a`
- Revision assertion: passed after detached checkout.
- Git archive SHA-256: `8e3395301f659b71e515f64f378c4c1dbdb5b8da8a6c76e4d8550afa1b4a6b3b`
- License: Apache-2.0
- `LICENSE` SHA-256: `73779e64d779249a335d2d7547541ab74b4901e1a9a112c7514b369b06ad1cf4`
- Module path: `github.com/go-mysql-org/go-mysql`.
- Go directive: `1.25.0`; the repository Go lane is locked to Go `1.26.5` on Linux/amd64.
- The tree contains 13 principal packages, 59 test files, and 282 static test functions.

## Public behavior and adapter boundary

The package is a broad MySQL network-protocol implementation, not a small pure
data utility. Its public surface includes:

- `client`: connection, authentication, TLS, compression, query execution,
  transactions, prepared statements, local-infile, and `database/sql`-style APIs;
- `mysql`, `packet`, and `serialization`: packet framing, result sets, field
  values, authentication data, GTIDs, positions, and binary protocol encoding;
- `replication` and `canal`: binlog streaming, schema inspection, incremental
  dumps, event decoding, and downstream handler callbacks;
- `server`: a fake MySQL server with handshake, authentication, query, and
  replication responses;
- `dump` and command packages: SQL dump parsing/writing and `mysqldump` execution.

Observed boundaries include TCP and Unix-socket MySQL servers, MySQL/MariaDB
authentication and TLS, compression, live query/result semantics, binlog and
replication streams, filesystem-backed dumps, the external `mysqldump` binary,
and downstream service callbacks. A separate verifier cannot import candidate
code directly, and no reviewed child-side typed protocol fixture is available
to model these stateful interactions deterministically.

## Dependency probe

The bounded no-network probe was:

```text
GOOS=linux GOARCH=amd64 CGO_ENABLED=0 GOWORK=off GOPROXY=off GOSUMDB=off GOTOOLCHAIN=local GOMODCACHE=/tmp/go-go-mysql-empty-modcache GOCACHE=/tmp/go-go-mysql-empty-cache go test -json ./...
```

It exited with code `1` before complete collection because module lookup was
disabled and the empty cache lacked the declared closure. Missing packages
included `filippo.io/edwards25519`, `github.com/goccy/go-json`,
`github.com/shopspring/decimal`, `github.com/pingcap/tidb/pkg/parser`, and
`github.com/stretchr/testify`. The module file declares 24 direct/indirect
requirements. No private module bundle was created by this lane.

## Blocker and remediation

Primary failure class: `verifier`; the dependency closure is a secondary
environment blocker. The task cannot enter the current Go production profile
without:

1. a complete hash-locked offline Go module closure and a reproducible image;
2. an approved child-side MySQL/MariaDB protocol fixture covering handshake,
   authentication, TLS/compression, queries, result sets, prepared statements,
   and error packets;
3. a bounded adapter for replication/binlog, canal callbacks, SQL dumps, and
   server-side protocol behavior;
4. a public-behavior denominator that excludes unsupported live-service paths
   rather than silently claiming the full upstream suite.

Until those prerequisites are reviewed and frozen, no Oracle, controls, reward,
or generated runtime is claimed. The candidate remains `blocked`.
