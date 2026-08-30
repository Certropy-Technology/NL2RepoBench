# `unist-util-is` authoring provenance

## Source and license freeze

- Upstream: `https://github.com/syntax-tree/unist-util-is`.
- Frozen revision: `82b9c2547dfa52e6078a546ab5a1c64bb9381480`.
- Git tree: `fbf540856b6541466090b6b4cb76e6e3050b3ed8`.
- Package version: `6.0.1`.
- Deterministic raw Git archive SHA-256:
  `e9136a0d23958fc6b29161c357dcbedf2e98d9478da87a9e77c2167a938403f4`.
- Root `license` is MIT; license SHA-256:
  `82974dbf2639d13edab95c32ed9cb6c0867ede272cd2e07ce47ce8548fe55c05`.
- The commit contains 14 tracked files and no submodules.

The private Oracle bundle fetches only this commit, asserts the resolved commit,
verifies the raw Git archive, and restores generated declarations whose four
SHA-256 hashes were captured from the successful frozen build. The model Agent
does not receive the Oracle bundle or source-host authorization.

## Build, API, and tests

The first full `npm test` attempt in the pinned minimal Node image reached
380/380 type coverage but failed in the Markdown formatter because that image
does not include Git. A bounded authoring-only remediation installed Git
2.39.5 in the temporary container. The repeated full suite passed under Node
24.19.0/npm 11.17.0 with 380/380 type coverage, 24/24 Node tests, and the
upstream 100% c8 threshold. Git is a development formatter dependency only and
is not required by the candidate runtime.

The frozen public surface is an ESM package with two named synchronous exports,
`is` and `convert`. The production contract contains 56 independent leaves for
package shape, node recognition, all documented selector forms, callback
binding, validation errors, and converted-check reuse.

## Dependency closure

The only runtime package is exact `@types/unist@3.0.3`, pinned by npm lockfile
version 3 with SHA-512 integrity. The private cache contains four regular npm
v3 cache entries and no lifecycle, native, optional, platform-specific, or
transitive packages. After cache population during authoring, a cold
`npm ci --offline --ignore-scripts --no-audit --no-fund` passed with Docker
networking disabled.

## Verifier boundary

The separate verifier copies and packs a bounded candidate tree, installs it
from the private npm cache, and invokes only the installed package root in
one-shot UID/GID 10001 child processes. A task-specific adapter reconstructs a
small declarative callback vocabulary and shared-object references inside the
child. Trusted Node and Python processes never import candidate code, and only
the verifier writes collection, grading, network, and reward artifacts.

## Gate status

Source validation, production compilation, Oracle, controls, evidence binding,
and network lint are completed after the corresponding receipts are recorded
in `production-evidence.json`. This lane does not run a model Agent, perform
independent review, integrate a dataset, or publish the task.
