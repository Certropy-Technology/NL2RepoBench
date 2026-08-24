# Fastify Authoring Evidence

## Source Freeze

- Upstream: `https://github.com/fastify/fastify`
- Revision: `4176096a31f5b4c31512c36f578b08a596a72435`
- License: MIT, from `package.json` and `LICENSE`
- Frozen checkout: `.nl2repo/authoring-work/node-author-direct-gpt-20260824-r1/fastify/source`
- Source archive digest and inventory are recorded in `.nl2repo/evidence/source-freeze.json`.

## Runtime Remediation

The upstream repository does not commit an npm lockfile and its development graph contains optional platform packages. A task-local runtime template removes only development metadata and retains the exact published runtime dependency ranges. npm 11.17.0 generated a lockfile v3 and cache; the closure is replayed with `npm ci --offline --ignore-scripts`. The upstream source is not modified.

Commands and logs:

- `npm install --package-lock-only --ignore-scripts --no-audit --no-fund --cache=.nl2repo/authoring-work/.../runtime-cache --registry=https://registry.npmjs.org`
- `npm ci --ignore-scripts --no-audit --no-fund --cache=.nl2repo/authoring-work/.../runtime-cache`
- Clean replay: `npm ci --offline --ignore-scripts --no-audit --no-fund --cache=.nl2repo/authoring-work/.../runtime-cache`

## Test Scope

The upstream checkout contains 233 test files and network/native/type/lint coverage that cannot be transferred through the JSON subprocess boundary. The private 14-leaf contract is a deterministic adaptation of the public Fastify core surface: route matching and methods, injection and JSON bodies, hooks, schema validation, errors, not-found handling, plugin prefix/encapsulation, and lifecycle/introspection. Every leaf is traceable to `instruction.md`; the full upstream suite remains inventory evidence, not a hidden denominator.

## Network Boundary

The final task uses the locked Node 24.19.0 image and `agent_network_mode = "no-network"`. The candidate has no source checkout, private tests, Oracle, or registry access. Runtime dependencies are supplied through the task-local private npm bundle and copied into the agent/verifier build contexts; npm commands are offline and ignore lifecycle scripts.
