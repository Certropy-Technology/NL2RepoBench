# Meros authoring status: blocked

## Project Description

The requested task targets Meros at commit `87ed69fe97f5a250ee6e8bec1a9ba458e16655f9`, a TypeScript package that parses `multipart/*` HTTP response streams into JSON or binary parts. The source revision and MIT license were frozen successfully.

## Supports

No runnable candidate contract is published while the complete offline build and test closure is missing. Agent, candidate, verifier, Oracle, and every control must use `network_mode=no-network`; runtime access to GitHub, npm, PyPI, Go proxy, and external services is forbidden.

## API Usage Guide

The intended future contract must cover the Node `meros(response, options?)` API, including multipart boundary extraction, JSON/text/binary bodies, chunk boundaries, headers, `multiple`, non-multipart passthrough, and stream cleanup. Browser behavior and TypeScript declarations require a separate child-side adapter contract.

## Implementation Notes

The frozen package has no runtime dependencies, but its upstream build and test closure requires pnpm packages including `bundt`, `typescript`, `tsm`, `uvu`, and `@n1ru4l/push-pull-async-iterable-iterator`. An offline installation attempt failed because the pnpm store lacks `@jridgewell/trace-mapping@0.3.25`. The missing closure must be injected as private, hash-locked artifacts before deterministic transpilation, test collection, Oracle execution, and controls can be performed.

This is truthful blocked evidence, not a production task. No generated `catalog/tasks/meros` runtime exists.
