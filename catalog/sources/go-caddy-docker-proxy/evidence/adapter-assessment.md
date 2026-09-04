# Adapter assessment

Status: blocked.

The public behavior is not limited to deterministic label parsing. `loader.go`
constructs one or more Moby clients from `DOCKER_HOST` or configured socket
paths, calls `Ping`, subscribes to `Events`, and launches an event monitor that
reconnects indefinitely. `generator/generator.go` then calls Docker container,
service, task, config, network, inspect, and Swarm-info APIs. `push.go` either
loads a Caddy config into the local process or sends an HTTP request to a
remote Caddy admin endpoint.

The upstream unit tests make generator behavior deterministic by injecting
`docker.ClientMock` and `docker.UtilsMock`. These are test-only structs and do
not form a supported external API. A verifier-supplied bridge that serialized
those mocks would therefore bypass the package's public Docker client creation,
socket, event, and runtime behavior. A real adapter requires a reviewed Docker
API fixture and a bounded Caddy admin/in-process runtime fixture. The current
bridge registry has no such task-specific adapter, so producing a fake JSON
bridge or granting `/var/run/docker.sock` would violate isolation and external
IO policy.

The frozen source's 50 test functions include three integration tests that
start Caddy or exercise HTTP/admin behavior. Their source-health success was
observed only after the module graph was fetched. With an empty module cache
and `GOPROXY=off`, compilation fails before collection. The complete private
Go closure is therefore also unresolved.
