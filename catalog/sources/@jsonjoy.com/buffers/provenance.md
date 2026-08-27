# `@jsonjoy.com/buffers` Authoring Provenance

## Source Freeze

- Upstream: `https://github.com/streamich/json-joy`
- Revision: `6ac8a8968260c88cb5e1819f177db4aab5897f7a` (`chore: release v18.28.0`)
- Exact source archive command: `git archive --format=tar 6ac8a8968260c88cb5e1819f177db4aab5897f7a`
- Exact full-repository archive SHA-256: `89c8a3db0edf738fb45e4205103a266fb40f121bc4477ceb062851f6ad67a2dd`
- Package license: Apache-2.0; `packages/buffers/LICENSE` SHA-256 is recorded in the task-local freeze evidence.
- No submodules.

The package contains 37 TypeScript source files and 9 upstream `.vi` test files.
The monorepo's tests require Jest/Vitest tooling and are ignored by the upstream
test regex for this package's verification mode. The fixed slice below is a
deterministic `node:test` black-box adapter over the public utility modules.

## Remediation and Build Context

The upstream package inherits its TypeScript configuration from the monorepo and
declares `json-pack-napi` only as a development dependency. The task-local Oracle
build creates an equivalent standalone TypeScript context and excludes the
unexported native `v19` experiment. The candidate dependency closure is a v3 npm
lock/cache bundle containing exact `tslib`, TypeScript, `@types/node`, and
`undici-types` artifacts. Installation uses `npm ci --offline --ignore-scripts`.

## Verifier Scope

The private tests freeze 28 leaves covering package layout, byte construction and
comparison, conversion and formatting, half-floats, ASCII/UTF-8 encoding and
validation, and representative pure-function edge cases. Tests call only the
candidate subprocess boundary; trusted code never imports candidate modules.
Class APIs remain explicit in the public contract but are excluded from the
JSON-only fixed slice because a generic one-call RPC cannot safely construct and
retain mutable objects between calls. Browser, benchmark, native-addon, and
monorepo-only surfaces are excluded as deterministic adaptation boundaries.
