# `go-burrow` Go authoring audit: blocked

## Project Description

Burrow is a Kafka consumer-lag monitoring service, not a self-contained Go
library. The frozen revision starts a configured service, consumes Kafka and
ZooKeeper state, evaluates consumer groups, serves HTTP endpoints, and can send
email or HTTP notifications.

## Supports

This source is intentionally blocked. No Harbor runtime, Oracle, private module
bundle, or separate verifier is claimed. The current Go production profile
requires a deterministic child-side adapter and a no-network, fixed-denominator
contract. Burrow's service and dependency contracts do not satisfy that profile.

## API Usage Guide

The root executable accepts `--config-dir` and then reads `burrow.toml` through
Viper. The exported library entry point is `core.Start(app, exitChannel) int`;
it blocks while starting coordinators for storage, evaluation, HTTP serving,
Kafka clusters, Kafka consumer offsets, optional ZooKeeper consumers, and
optional notifiers. The HTTP surface includes Kafka, consumer, lag, and
Prometheus endpoints, but their results depend on live configured services.

The source also exposes protocol interfaces and data types under
`core/protocol`, while the useful implementation packages are under
`core/internal` and cannot be imported by an external candidate module.

## Implementation Notes

The source is frozen at commit
`66bdb0566fdeb14251a53eb7f6cb4ed4036d16ed` from
`https://github.com/linkedin/Burrow`.

The archive digest is
`sha256:1f4477129cbeffec5013d106374f074e460e14c5f721f3253c45f35f31a36035`.
The Apache-2.0 `LICENSE` digest is
`sha256:cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`.
The tree contains 67 Go files, 26 test files, 237 test functions, and 9,213
non-test Go source lines.

The source-only no-network probe used an empty Go module and build cache and
failed before test collection because GOPROXY was disabled and the module
closure was not available. A normal probe with this host's pre-existing module
cache passed, but that does not establish a reproducible offline dependency
bundle.

### Blocker

Primary failure class: `verifier`.

The current separate Go verifier cannot faithfully express Burrow's live Kafka,
ZooKeeper, HTTP server, notifier, configuration, and long-running lifecycle
semantics without an approved deterministic service fixture and child-side
protocol. Replacing those services with a fake in-memory model would define a
new API contract rather than preserve the frozen project behavior. The missing
private module closure is a secondary `environment` blocker.

### Remediation

1. Approve a deterministic Kafka/ZooKeeper/service fixture and a bounded
   child-side adapter, or explicitly exclude the service from this benchmark.
2. Materialize and hash-lock the complete Go module closure, including Sarama,
   go-zk, Viper, Prometheus, notifier, and transitive modules.
3. Add public-behavior tests for configuration, HTTP responses, consumer lag,
   lifecycle shutdown, and notifier failure handling; exclude tests bound to
   private internals or live infrastructure.
4. Re-run source collection, production compilation, Oracle, and controls only
   after those contracts are reviewed.

Until then this task remains blocked. No generated `catalog/tasks/go-burrow/`
projection exists.
