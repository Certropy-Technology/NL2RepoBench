# orjson authoring provenance

- Upstream: `https://github.com/ijl/orjson`
- Frozen revision: `6737895a1a4e3e26df0569a40147893a786f9a58` (`3.12.0`, 2026-08-14).
- Canonical unprefixed `git archive --format=tar HEAD` SHA-256:
  `sha256:d576d84f7005c9e4b624e3f990c8fd3c07748370290eb94fb5fb7f4e1339cb61`.
- License files: `LICENSE-APACHE` SHA-256 `0664b1761d2ee078e4222027d3909daa57bbe446469a01fa5a260439b72d243e` for the tracked source file inventory was separately checked; the declared SPDX expression is `MPL-2.0 AND (Apache-2.0 OR MIT)` and all three license files are present.
- Source inventory: 620 files, 105,493 total lines; 82 Rust files and 8,732 nonblank Rust lines; 32 upstream test modules and 1,262 test functions.
- Native build probe: Rust/cargo 1.97.1 and maturin 1.10.2 built `orjson-3.12.0-cp312-cp312-manylinux_2_34_x86_64.whl` successfully from the frozen checkout. Wheel SHA-256 is `sha256:144297495446ae65a0e69ef24864e357c74375401357c36e942977b971cec36b` and size is 295,539 bytes.
- Environment: CPython 3.12.14 on Debian 13 amd64, base image digest `sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254`.
- The package's Rust build requirement is newer than Debian 13's default apt Rust package. The trusted reference wheel was therefore built with the verified Rust 1.97.1 toolchain; candidate/verifier run phases remain offline and do not install Rust or fetch source.
- The Oracle bundle is an immutable private tar with digest `sha256:eaef2e408ae249021f4bb30e8cf39f1c745771b31b309468652f897ac66670ef` and size 307,200 bytes; it contains the 295,539-byte wheel, a minimal installable project manifest, and its digest-checked solve script.
- The private verifier bundle was refreshed as immutable digest `sha256:a1dd8736c53ada9217f9fe1f6b32c020b4b2362266fbb236796501ac707b0449` after correcting subprocess observation of byte-returning `dumps` calls and the TypeError alias contract.
- Private verifier uses 26 fixed `custom-json-v1` leaves and imports candidate code only through the trusted subprocess client. Oracle/control receipts are intentionally deferred to the integrator because this authoring lane cannot start Harbor runs.
