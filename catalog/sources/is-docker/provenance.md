# `is-docker` Provenance

- Upstream: `https://github.com/sindresorhus/is-docker`
- Frozen revision: `59379f14b6dda26a0167fce55d80bf546857f92d`
- Git tree: `373bf4a1759c6c2e56b1f1755689e8c9b526e3f1`
- Package version: `4.0.0`
- License: MIT
- License SHA-256: `5c932d88256b4ab958f64a856fa48e8bd1f55bc1d96b8149c65689e0c61789d3`
- Prefixed `git archive` SHA-256: `4b0b0b2f7949858e2c44da8b3dd2224ccc95eb8545674c867147ae93e6381cb5`
- Tracked files: 13; submodules: none

The source checkout is detached at the exact revision. Its `.npmrc` disables
lockfile generation and package metadata declares development dependency ranges;
neither is reused as the candidate closure. The task instead uses an independent
zero-dependency npm v3 lock and empty offline cache.

## Ground-Truth Probes

| Stage | Runtime | Exit | Result |
| --- | --- | ---: | --- |
| source freeze | Git checkout and prefixed archive | 0 | exact revision, tree, archive, and MIT license digests recorded |
| upstream suite | host Node 22.23.1 / npm 10.9.8 | 0 | XO and five `node:test` leaves passed |
| upstream suite | Node 24.19.0 / npm 11.17.0 image | 0 | XO and five `node:test` leaves passed |

The upstream test suite mocks `node:fs`, which cannot cross the production
separate-process boundary as native module state. The private verifier therefore
uses a bounded JSON adapter that models only the three documented marker results
and their first-call cache semantics. Oracle acquisition remains private: it
fetches only the exact revision, checks the resolved commit and prefixed archive
digest, then adds the adapter without changing the upstream default-export
decision logic.
