# Cheerio instruction revalidation blocker

- Source digest validated before this evidence update: `sha256:bf12074602aa7c8a0d3883fc7607d7ebf6fe3e192702889d43c5fb3d702c899a`.
- Two production compiles completed with `toolchain.node.lock.toml`, the absolute parent CAS, and `--allow-private`; outputs were byte-identical. The canonical manifest digest is `sha256:fae1fa45bbead289b53ec4a20a2ee36f993f386164ce7731279996e901909d07`.
- The compiled Oracle `solve.sh` only copies the private prebuilt package into `/workspace` and performs local file checks. No runtime source fetch, registry install, DNS, or external service access is used.
- Fresh Harbor Oracle run `cheerio-revalidation-oracle-20260905/cheerio__bwmsQuV` passed `51/51`, reward `1.0`, valid `true`, with `public_network_available=false`.
- The current source has no `harbor/controls` directory and the compiled bundle has no `controls/` directory. `prepare-control` therefore cannot create the required Node `empty`, `stub`, `forgery`, or `offline` bundles; this is a verifier/control-contract blocker, not a candidate failure.
- Historical `production-evidence.json` was not rewritten because its receipts are not durable in this worktree and the required control matrix cannot be rerun from the current source. Lifecycle and historical evidence remain unchanged.

## Remediation

Add task-local, standalone NoNetwork control scripts for `empty`, `stub`, and `forgery` (plus an offline run contract), compile a new final bundle, and rerun the complete Oracle/control matrix. Persist every receipt under this directory before updating production evidence.
