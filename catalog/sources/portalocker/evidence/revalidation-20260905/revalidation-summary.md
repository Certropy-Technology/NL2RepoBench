# portalocker instruction-migration revalidation

- Queue/source digest was checked before mutation and matched `sha256:642174a73d8c1a537186b6e24b4833f49aade86a4dbf6b11c182f93c9ec6ef3`.
- All four declared private artifacts were recovered locally and verified by exact size and SHA-256: build lock 1,836 bytes, source archive 1,239,040 bytes, verifier bundle 20,480 bytes, Oracle bundle 1,249,280 bytes.
- Two production compiles with the locked Python toolchain succeeded without `--allow-incomplete`; all 61 files were byte-identical and both manifests have SHA-256 `sha256:6e2725c74559cf756f0d1996d9e23275cdaf1116b02c4680151d34c21149eb0b`.
- The first Oracle attempt failed before trial creation with `EnvironmentStartTimeoutError` after the bounded 600-second environment-start limit. A single bounded retry succeeded.

## Fresh NoNetwork matrix

| run | valid | collected | passed | reward | classification |
| --- | --- | ---: | ---: | ---: | --- |
| Oracle retry | true | 32 | 32 | 1.0 | none |
| empty | true | 0 | 0 | 0.0 | model / candidate-installation-failed exception |
| stub | true | 32 | 0 | 0.0 | model negative control |
| forgery | true | 32 | 0 | 0.0 | verifier-owned grading; workspace forgery did not affect result |
| offline | covered by Oracle receipt | — | — | — | public network unavailable; standalone prepare-control kind unsupported |

Every fresh verifier receipt reported `public_network_available=false` with both the numeric-IP and PyPI probes false. The fixed denominator was 32 for Oracle, stub, and forgery; stub and forgery both remained at or below 0.20. The empty result is the permitted installation-failure exception.

The existing `production-evidence.json`, lifecycle, task metadata, generated projection, shared CAS, and reports were not modified. Private payload bytes and run trees were not copied into this source evidence; persisted paths use placeholders.
