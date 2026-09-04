# Recreate caddy-docker-proxy: blocked authoring handoff

## Project Description

The pinned `github.com/lucaslorentz/caddy-docker-proxy/v2` revision is a Caddy
plugin that watches Docker and Swarm metadata, converts `caddy.*` labels and
Swarm configs into Caddyfile content, and reloads local or remote Caddy admin
endpoints. This candidate is currently blocked from the production authoring
lane.

## Supports

- Requested immutable revision: `d246679c72e1c3d2ef0e610503e1c2f74581978b`.
- Target runtime would be Linux/amd64 with Go `1.26.5`, CGO disabled, and no
  network during candidate or verifier execution.
- A production task would need a hash-locked private Go module closure for
  Caddy, Moby Docker, Sprig, Zap, Godotenv, and their transitive modules.

## API Usage Guide

The exported surface includes `CreateDockerLoader`, `DockerLoader.Start`,
`CreateGenerator`, `CaddyfileGenerator.GenerateCaddyfile`, Caddy module
registration, Caddyfile `FromLabels`, `Unmarshal`, `Process`, and the Docker
client wrapper. The core loader contract is not a pure data transformation:
`Start` constructs Docker clients from `DOCKER_HOST` or configured Unix/TCP
sockets, pings each server, subscribes to Docker events, reads container,
service, task, network, and config metadata, and pushes generated configuration
through Caddy's local runtime or an HTTP admin endpoint.

The repository's useful generator tests inject `docker.ClientMock`, but that
type is test-only and is not a public package contract. Replacing Docker with a
JSON fixture in a verifier would test a newly invented adapter rather than the
requested package behavior. A faithful adapter would need a reviewed Docker
API/socket fixture or a separately approved fake daemon protocol, plus a
bounded Caddy runtime/admin fixture.

## Implementation Notes

This task must remain blocked until all of the following are resolved:

1. Materialize and hash-lock the complete Go module closure for offline build.
2. Define an approved child-side Docker daemon/API fixture covering ping,
   events, containers, Swarm services/tasks/configs, networks, and inspect
   responses without granting the candidate the host Docker socket.
3. Define a reviewed Caddy runtime/admin adapter covering local `caddy.Load`,
   remote admin POSTs, config validation, reload behavior, and log/runtime
   state.
4. Re-collect a fixed, source-traceable test denominator after the adapter is
   designed. The upstream revision has 50 static test functions across 13 test
   files; several integration tests start Caddy or use HTTP, so this count is a
   source-health observation, not a production denominator.

No generated Harbor runtime, Oracle, controls, or reward is provided while the
adapter and dependency blockers remain unresolved.
