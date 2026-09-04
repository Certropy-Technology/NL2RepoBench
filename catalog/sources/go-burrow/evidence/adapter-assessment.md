# Adapter assessment

## Result

`go-burrow` is blocked under the current Go production profile. No adapter or
Harbor verifier was authored because doing so without a reviewed service
fixture would change the project contract.

## Observable service dependencies

- `main.go` requires a configuration directory and reads `burrow.toml`.
- `core.Start` starts storage, evaluator, HTTP server, Kafka cluster, and Kafka
  consumer coordinators, then blocks until a signal arrives.
- Kafka cluster and consumer modules use Sarama to connect to brokers, inspect
  topics and offsets, and consume `__consumer_offsets`.
- ZooKeeper consumers use `github.com/linkedin/go-zk`, watches, and configured
  `/consumers` metadata paths.
- HTTP handlers expose cluster, topic, consumer, status, lag, delete, and
  Prometheus behavior derived from the running coordinator state.
- Email and HTTP notifiers perform external side effects and have their own
  retry/error behavior.
- The Docker Compose reference stack requires Kafka and ZooKeeper services.

The behavior includes network I/O, service readiness, background goroutines,
signal shutdown, configuration and filesystem state, and optional notifier
side effects. These are not representable by the current one-leaf typed JSON
bridge without a task-specific deterministic multi-service fixture.

## Testability

The frozen tree has 26 Go test files and 237 test functions. Many tests use
Sarama or ZooKeeper mocks and directly import `core/internal` packages, while
the candidate-side bridge cannot import those internal packages from an
external module. The root `main_test.go` contains only a dummy test. Adapting
the internal tests wholesale would test private implementation details rather
than the public service contract.

## Decision

Primary failure class: `verifier`. Secondary failure class: `environment` due
to the absent private module closure under a clean no-network cache. Reopen only
after a deterministic service fixture, a reviewed child-side protocol, public
behavior test inventory, and a hash-bound offline module bundle are approved.
