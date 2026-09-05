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
in the parent private artifact store and are intentionally absent from the public catalog.

## Instruction migration revalidation (2026-09-05)

- The validated catalog source digest is `sha256:bec3a67067d3573b9229c7d88fd64db8d209ffb5fe1812a46c2c9992bee9dcd6`.
- The source was compiled twice with `toolchain.node.lock.toml` and Harbor `0.21.0`; the
  final bundles were byte-identical. The final canonical manifest digest is
  `sha256:68381e8a174fd7a604a8116c52111f787be279fe004e322601add3e1f71279d6` and the
  manifest file hash is `sha256:1bb18520089b45bffad19bc2ae571e60439e3a1f876322812cb7ac3abb6297c3`.
- A standalone empty control was added before compilation so the final matrix used one
  unchanged bundle for Oracle, empty, stub, and forgery.
- Oracle collected and passed `12/12` with reward `1.0`; empty produced the allowed
  candidate-installation failure with `0/12` collected and reward `0.0`; stub and forgery
  each collected `12/12`, passed `0`, and scored `0.0`. Forgery-created candidate grading
  files did not affect verifier-owned grading.
- All final verifier network receipts reported `public_network_available=false`. Compact,
  hash-bound summaries for the bundle and every run are stored under
  `evidence/revalidation-20260905/` and are the only paths referenced by production evidence.
