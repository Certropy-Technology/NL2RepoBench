# Network Policy Contract

`network_policy` is a catalog declaration, not a generated Harbor field. Human
edits belong in `catalog/sources/<task-id>/task.toml`; `catalog/tasks/` and the
Harbor bundle are projections produced by the compiler or migration integrator.

The compiler is authoritative for the projection: a declared policy overrides
legacy `harbor.agent_network_mode` values when a canonical manifest is built.
Do not repair a drifted generated task by editing its `task.toml` alone; update
the source declaration and recompile the task.

## Default

Every task that can run as an agent declares:

```toml
[environment.network_policy]
mode = "no-network"
offline_dependencies = "preinstalled-image"
reference_source_fetch = "forbidden"
reason = "Dependencies are installed during the Docker build phase."
```

`public` is not an admissible policy. Build-time package downloads are allowed
when the Dockerfile uses pinned or hash-locked inputs. The run-time agent and
verifier environment should not contact a package registry.

## Allowlist

Use `allowlist` only when a dependency or the in-container model client cannot
be provisioned during build. Every entry must be an exact hostname. Wildcards,
URLs, ports, generic mirrors, GitHub, raw GitHub, GitHubusercontent, and other
code hosts are rejected by the domain validator.

Model-provider hosts are normally supplied per run with Harbor's
`agent.extra_allowed_hosts`; they should not be hard-coded into every task.
Registry hosts are an exception and produce a lint warning because the package
should normally be moved into the image or a private artifact.

## Compiler behavior

The compiler resolves the catalog policy into the Harbor agent profile:

```text
catalog task.toml [environment.network_policy]
    -> canonical EnvironmentLock.network_policy
    -> HarborExecutionProfile.agent_network_mode/agent_allowed_hosts
    -> Harbor task.toml + egress-sidecar-managed agent network
```

The compiler therefore owns the generated runtime projection. A policy change
must not be implemented by editing generated `catalog/tasks` files alone.
Agent services must not declare Compose `network_mode` or `networks`: Harbor
respects explicit task-authored networking and then cannot route that service
through its egress sidecar, so run-scoped `--allow-agent-host` overrides would
not reach the model Provider or Oracle source host. The separate verifier keeps
its explicit `tests/docker-compose.yaml: network_mode: none` override because it
never receives a run-scoped host authorization.

## Oracle

The Oracle is the reference implementation and may fetch the frozen revision
from its `solution/` upload. The model agent never receives `solution/`, and a
model run does not receive the Oracle source host authorization. Oracle scripts
must pin the full revision and verify `source_digest` (or the documented tag-ref
exception for `export-subst` projects).

Check the whole catalog with:

```bash
uv run nl2repo task lint-network
```

The command is static and must report zero errors before a task is compiled or
run. Warnings identify missing dependency closure, run-time registry access, or
Oracle host authorization that still needs review.
