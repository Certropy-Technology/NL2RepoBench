# Arrow Authoring Audit

- Candidate: `https://github.com/arrow-py/arrow`
- Frozen revision: `2224255c4acc594d734cef0bbc83360452a67983`
- License: Apache-2.0; frozen LICENSE bytes are 11,341 bytes with SHA-256
  `b481f87296cb0abdb13fd8cbb94b14c328be880ec9e68547a61b84dacffd067a`.
- Source archive: `sha256:8c08b167afc01268080ba13e5e1cf17223ec2fe12512fd298f03132270f7cda6`.
- The source-only pytest run collected 1,902 leaves and passed all 1,902 on
  CPython 3.12.11 with pytest 9.1.1. The Harbor verifier intentionally uses a
  smaller, independently enumerated 48-leaf JSON contract to preserve the
  candidate subprocess boundary and fixed denominator.
- Static inventory and raw probe records are under `.nl2repo/evidence/arrow/`;
  private verifier, dependency lock, and Oracle bundle are under
  `.nl2repo/artifacts/private/` and are referenced by digest in `task.toml`.
