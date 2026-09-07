# rust-semver provenance

- Upstream: <https://github.com/dtolnay/semver>
- Frozen ref: tag `1.0.27`, which peels to commit
  `6ed8561154715b2c34df417a2052597d586f2c43`.
- Archive: `git archive --format=tar --prefix=semver/` at that commit,
  `sha256:193fa1e8e7fd3f5bd3f5fcf911df523b4d1cd59c33fba7a079bec9dfaf761594`
  (153600 bytes).
- Licence: `MIT OR Apache-2.0`. `LICENSE-MIT` is
  `sha256:23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`
  (1023 bytes) and `LICENSE-APACHE` is
  `sha256:62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a`
  (9723 bytes).
- Offline baseline: `cargo test --lib --tests --locked --offline` passes 34 tests
  with zero failures once the crate is installed in the dependency-free contract
  shape published by `instruction.md`.
- Build script: the revision carries a 23-SLOC `build.rs`, recorded as
  `build-script-command`. It runs `rustc --version` to detect the compiler minor
  version and may emit `cargo:rustc-check-cfg`. It performs no network access and
  writes no files, so it stays inside this lane's bounded build-script contract.
- Packaging relaxation, documented rather than hidden: the published manifest
  declares an optional `serde` integration (`serde_core`) that cannot be resolved
  inside the dependency-free offline closure. The Oracle therefore installs the
  frozen `src/` plus the dependency-free contract manifest that the public
  instruction already requires. No behaviour named by the task API changes, and
  the optional Serde surface is explicitly out of contract in
  `api-inventory.json`.
- Task identity: this is a new Rust lane task. The pre-existing `semver` source is
  the blocked Node/npm `node-semver` task and is left byte-identical to its
  committed state; `rust-semver` follows the `go-semver` convention for a
  cross-ecosystem name clash.
