# PyYAML authoring audit

## Frozen source

- Upstream: `https://github.com/yaml/pyyaml`
- Revision: `34a9bf82357f4952d8f194a5a31f1c39743652d0`
- Source archive: `git archive --format=tar 34a9bf82357f4952d8f194a5a31f1c39743652d0`, SHA-256
  `sha256:18387c6163aa3de3221240cade5f77768963c1096061119d67503462049eab68`,
  1,218,560 bytes.
- License: MIT. `LICENSE` SHA-256 is
  `sha256:8d3928f9dc4490fd635707cb88eb26bd764102a7282954307d3e5167a577e8a4`.

## Inventory and probes

- The frozen archive has 642 regular files (658 members including directories),
  including 17 Python modules under `lib/yaml`, the checked-in Cython source/C
  file, packaging backend, examples, and 602 regular test/fixture files.
- Public module inventory covers root load/dump/scan/parse/compose/emit/
  serialize and registration functions, five Python loader classes, three
  dumper classes, event/token/node families, parser/constructor/resolver/
  representer and reader components, plus typed exceptions.
- Upstream pytest collection under `pytest -c /dev/null --collect-only -q
  tests` collected 1,287 leaves. With `PYTHONPATH=lib` and no LibYAML extension,
  `pytest -c /dev/null -q tests` passed 1,287/1,287.
- Forcing `PYYAML_FORCE_LIBYAML=1` without the optional extension failed during
  collection as designed; this is excluded from the task denominator because
  the production environment intentionally omits LibYAML headers and libraries.

## Runtime and dependency closure

- Runtime: CPython 3.12.14 on `python:3.12.14-slim-bookworm`, base digest
  `sha256:356b0d18f9385f4bdcc673af60e1e64c9d1504952e4ec36ee32044c722a6bc4e`.
- Candidate build/test closure is the private hash lock
  `provenance/requirements.lock.txt`, 7,323 bytes, digest
  `sha256:d226ffcdb54f7b30c35189714c0af444c46d3697c23efcb1f838808e1c3a05e9`.
- The optional C extension is not a runtime dependency. The task uses pure
  Python behavior so it remains reproducible without a system package.

## Verifier and scope

- Production verifier protocol is `custom-json-v1`, with 64 deterministic
  child-side scenarios covering the public contract and the frozen merge-key
  regression.
- Candidate code is installed into candidate-owned site-packages and invoked by
  an unprivileged subprocess. The root verifier owns collection, JUnit, grading,
  reward, and network reports.
- The custom scenarios are a bounded child-side adaptation of the upstream test inventory;
  the full upstream collection result is retained as provenance and the public
  specification describes every behavior exercised by the 64-leaf task contract.
- The trusted Oracle clones only `github.com` under a run-scoped Oracle host
  authorization, resolves the exact commit, recreates the archive, and rejects
  any digest mismatch before populating `/workspace`. Model Agent runs receive
  neither the Oracle upload nor the source-host authorization.

## Current Harbor evidence

- The current production compile contains 58 declared files. Its bundle
  manifest SHA-256 is
  `sha256:7df52d9393353b6b229c11306e2914a5056f16cc600af0d0fc4433804f660ce6`
  and its canonical manifest digest is
  `sha256:6acb6db1fef711c6d210c5180985320114314df8a72ffbe359b0256951c43928`.
- Harbor 0.21.0 ran the current bundle once as Oracle: `64/64`, reward `1.0`,
  valid, and public network unavailable. Empty, stub, forgery, install-timeout,
  call-timeout, and offline controls are bound by digest in
  `production-evidence.json`.
