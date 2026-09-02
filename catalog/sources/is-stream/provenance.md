# `is-stream` Provenance

- Upstream: `https://github.com/sindresorhus/is-stream`
- Frozen revision: `ab06c4acc9dce4dcadc9dfc6416e1be2c836862d`
- Git tree: `dc27186d72f0b08b51a9f7920a6a06b7bdb69665`
- Package version: `4.0.1`
- License: MIT
- License SHA-256: `5c932d88256b4ab958f64a856fa48e8bd1f55bc1d96b8149c65689e0c61789d3`
- Prefixed `git archive` SHA-256: `465680c19959fc1c1f85702de085b7118845e584ea797653f90c1130d550e3fd`
- Tracked files: 13; submodules: none

The source checkout was detached at the exact revision. Upstream metadata has
no runtime dependencies and requires Node 18 or newer. Its `.npmrc` disables
package-lock generation, so development ranges are not reused as the candidate
runtime closure. The task has an independent dependency-free npm v3 lock and
empty offline cache.

## Ground-Truth Probes

| Stage | Runtime | Exit | Result |
| --- | --- | ---: | --- |
| source freeze | Git checkout and prefixed archive | 0 | exact revision, tree, archive, and license digests recorded |
| upstream suite | Node 22.23.1 / npm 10.9.8 | 0 | XO, AVA 29/29, and TSD passed |
| upstream suite | Node 24.19.0 / npm 11.17.0 | 0 | XO, AVA 29/29, and TSD passed |

The private verifier converts the native-object test surface into 32 bounded
JSON scenarios. Oracle acquisition remains in `solution/solve.sh`: it fetches
only the exact commit under the trusted Oracle source-host override, asserts
the resolved revision, and verifies the prefixed archive digest before writing
the candidate workspace.
