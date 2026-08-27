# iso8601 Authoring Provenance

- Upstream: `https://github.com/micktwomey/pyiso8601`
- Frozen commit: `00c9262b9ad141f287b3263be7f2244fa01988c2`
- Source archive: unprefixed `git archive --format=tar HEAD`
- Source SHA-256: `6253d109a195cd118c204e64b513b14d8d07e0293c6089bf1dd1167cc2e2a97f`
- License: MIT, from `LICENSE` at the frozen commit
- Authoring runtime: CPython 3.12.11, uv 0.11.32, Debian 12 amd64
- Upstream baseline: 47 collected, 47 passed
- Production denominator: 31 deterministic private verifier leaves
- Runtime dependency closure: none; build closure is hash-locked `poetry-core==2.1.3`
- Harbor/toolchain target: Harbor 0.21.0, schema 1.4, `toolchain.lock.toml`

The Oracle solution fetches only the full pinned commit, asserts the resolved revision, creates the same unprefixed archive, verifies its SHA-256, and extracts it into `/workspace`. This solution bundle is private and is uploaded only for `-a oracle`; task metadata remains `no-network` and contains no Agent allowlist hosts.
