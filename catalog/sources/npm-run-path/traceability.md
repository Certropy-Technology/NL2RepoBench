# `npm-run-path` traceability

Frozen revision: `b9128591fc59429d8b0df7047d5283f259dc5e77`.

| Public contract | Private verifier group | Frozen source basis |
| --- | --- | --- |
| ESM package name, version, two named exports, and declarations | package contract | `package.json`, `index.js`, `index.d.ts` |
| Parent `node_modules/.bin` entries, order, switches, and deduplication | `npmRunPath` path construction | `index.js` and upstream AVA leaves 1-4, 9-10 |
| Executable directory insertion, relative resolution, and deduplication | `npmRunPath` path construction | `index.js` and upstream AVA leaves 12-25 |
| Empty, delimiter-only, leading-empty, and trailing-empty PATH handling | `npmRunPath` path construction | `index.js` and upstream AVA leaves 26-28 |
| String and file URL `cwd` and `execPath` values | both API groups | declarations and upstream AVA URL leaves |
| Environment clone, PATH update, unrelated keys, and Linux key casing | `npmRunPathEnv` cloning and path selection | `index.js`, `path-key`, and upstream AVA leaves 5-8 |
| Native `TypeError` behavior and deterministic repeated calls | errors and determinism | direct frozen implementation probes |

The private suite has 33 unique leaves. Every documented runtime export is
invoked through a bounded UID-separated child. The trusted `node:test` process
receives JSON only and owns TAP collection, grading, network evidence, and
reward output.
