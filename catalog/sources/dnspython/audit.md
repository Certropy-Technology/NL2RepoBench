# dnspython authoring audit

- Candidate: `dnspython`
- Upstream: `https://github.com/rthalley/dnspython`
- Frozen revision: `b723a83a2f192deda4aa341a1447689967e97889`
- Source archive: `git archive --format=tar HEAD`, 2,478,080 bytes,
  `sha256:4babaa40d1ee3c4c92d3d0abc9d16ca29cac08130ef60e83d820fb2961c9d53c`
- License: ISC, verified from `LICENSE` and `doc/license.rst`.
- Upstream package metadata: version `2.9.0dev0`, `requires-python >=3.10`,
  no runtime dependencies, build backend `uv_build`.
- Inventory: 159 Python modules under `dns/`, 555 public top-level AST
  symbols, 54 upstream `test_*.py` files.
- Scope adaptation: live resolver, DoH/DoQ, transfer, DNSSEC, platform and
  external-service tests are excluded from the deterministic offline slice.
  The public instruction states this boundary and the 20-leaf verifier covers
  only locally reproducible behavior.
- Upstream collection probe: `python -m pytest --collect-only -q -p no:cov`
  exited 4 because the checkout's `addopts` requires pytest-cov options not
  installed in the minimal authoring environment. This is recorded as a
  collection-environment observation, not a package blocker.
- Reproducible collection with `-o addopts=''` collected 1,418 tests; the
  deterministic offline core subset ran 693 tests and passed 693 tests.
- Authoring production compile generated a 56-file closed-world bundle with
  canonical manifest digest `sha256:61f6fe1b954631ded9d496c3ce9fec3e31afca96213184c4655885a156c3dea9`.
- Private CAS refs: dependency lock
  `sha256:5d512b9d962906055568862b5f8f45fe4344b394d49933c24559ad020c7f0c21`,
  verifier bundle
  `sha256:18cd6998c3c28e48867eacda73787a11b1356f1cf1d24860775ded00902baf29`,
  and Oracle bundle
  `sha256:c3493ea23bf2bdc0d755f6611306fbfe36139b0e1a078d6517d300cc6486c2c4`.
