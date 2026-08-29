# httpcore Authoring Record

## Freeze

- Upstream: `https://github.com/encode/httpcore`
- Revision: `10a658221deb38a4c5b16db55ab554b0bf731707`
- License: BSD-3-Clause, `LICENSE.md` SHA-256 `fdcb59154c74cbaba16a11242f7740bea9f23d6feb5547917d8c5f94a80392a5`
- Source archive: private artifact `sha256:8af2769a68cdd7e3b25786f439228ed9b8eed2fb7fb5076d9b173d93d2bc6143`, 634880 bytes

## Probes

The upstream checkout contains 153 test definitions. A full collection probe
collected 120 tests but failed because the isolated authoring interpreter lacked
Trio and the source's strict marker configuration rejects the missing marker.
The project also has live integration and proxy/socket tests. These are not
silently counted as passing. The frozen task instead uses 24 deterministic
MockStream/MockBackend cases in a private subprocess verifier, covering the
stable public transport behavior without DNS or external services.

The candidate closure is a 3,653-byte hash-locked pip requirements file for
`anyio`, `certifi`, `h11`, `h2`, `hatch-fancy-pypi-readme`, `hatchling`,
`hpack`, `hyperframe`, and their build dependencies. It is attached to the local
CAS as private artifact
`sha256:dc2a13a34eb0da9ba22a1de076a125e02a98403b015d5729ebfdf24dd51733b5`.

The separate verifier bundle is private artifact
`sha256:213c0497a6559a4125519f8bb6b6ae41caa969ed81504ef9c8330e8492306856`.
Each case runs in a UID-isolated child and emits only a fixed scenario verdict;
trusted grading remains verifier-owned.
