# better-sqlite3 provenance

- Upstream: `https://github.com/WiseLibs/better-sqlite3`
- Frozen revision: `f8e2d541208281368129929a96f70f937c0735ef`
- Git archive digest: `sha256:b831518db05ed246880131c6faca8dd775bb7f713dc29a76e51f53ba8c5602ab`
- License: MIT, verified from the frozen `LICENSE` file.
- Upstream package: `better-sqlite3@13.0.3`, Node `>=22`, native `node-gyp` addon.
- Upstream baseline: generated a local npm v3 lockfile, `npm ci`, `npm run build-release`, and `npm test` on Node `v22.23.1`; result `332 passing`.
- Deterministic adaptation: Node `24.19.0` standard-library `node:sqlite`, with a CommonJS root export and a private JSON scenario bridge. No native addon, SQLite download, lifecycle build, runtime dependency, or source clone is available to the model agent.
- Runtime image: `docker.io/library/node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`, `linux/amd64`, glibc.

The private Oracle, tests, command plan, and empty npm bundle are content-addressed
under `.nl2repo/artifacts` and are intentionally absent from the public catalog.
