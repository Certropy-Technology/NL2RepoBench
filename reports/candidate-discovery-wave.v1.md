# Candidate Discovery Wave v1

This report records the source pool used for the fourth authoring wave. It is a
discovery artifact, not a publication approval. Every candidate still requires
source freeze, final collection, offline dependency closure, private verifier
artifacts, Oracle and controls.

## Python first-wave candidates

| Task | Exact commit | License | Primary risk |
| --- | --- | --- | --- |
| `doit` | `1f9cbbce78a93f96a35abf2db5425361e2abf142` | MIT | timestamps, subprocesses, plugins |
| `typer` | `9a7b2e83f6b62c750d6026b0de9ebf2026a8b8fa` | MIT | CLI/Rich/Windows matrix |
| `python-fire` | `716bbc23d7eca949fdb682172283c8d18f742cb6` | Apache-2.0 | introspection and terminal formatting |
| `mashumaro` | `0ad3eaed34f09e4a361613b607aa78e9a51d9999` | Apache-2.0 | generated code and optional codecs |
| `sqlite-utils` | `56dd09702fdb9e899f577ffd51693c1f2176cb08` | Apache-2.0 | SQLite/FTS/GIS/plugins |
| `remarshal` | `2300f5dfc39411020c86ade0d202aaea2897ccf0` | MIT | eight format dependencies |

Initial scopes should prefer local deterministic CLI/API behavior and explicitly
exclude external services, native/GIS integrations, interactive terminals and
unfrozen optional codecs.

## Node first-wave candidates

| Task | Exact commit | License | Primary risk |
| --- | --- | --- | --- |
| `json5` | `b935d4a280eafa8835e6182551b63809e61243b0` | MIT | old dev tooling/build scripts |
| `jsonrepair` | `4a80ed87fb1155db064945bc2aa4f6b4f4e89c27` | ISC | generated ESM/CJS build output |

Both are promising JSON string-in/string-out candidates for the Node v2
subprocess boundary. Runtime dependency closure, lifecycle policy, generated
output provenance and adapted `node:test` denominator remain unproven.

## Screening rules

- No floating branch, tag, latest or registry-only source reference.
- No hidden tests, private npm cache, Oracle bytes or secrets in public task files.
- `npm ci --offline --ignore-scripts`/Python equivalent must use a reviewed,
  content-addressed closure, not a warm local cache.
- Candidate imports remain in an unprivileged child process; callbacks, class
  instances, streams, cycles and native/browser behavior require a task adapter
  or explicit exclusion.
- Python and Node candidates remain separate dataset/version contracts.
