# `globby` Authoring Provenance

Status: `controls-passed` / awaiting downstream Agent Run review.

## Source and license lock

- Upstream: `https://github.com/sindresorhus/globby`
- Frozen revision: `46cf13ff8bf5f0e0db96c4985faf83a59d194777`
- Commit tree: `c40d49f0f85e84b53b838a9e66bd4085260e0a48`
- Commit subject: `16.2.4`
- Source archive: `git archive --format=tar HEAD`
- Source archive SHA-256: `4d48f46f1a05cc55f3918b99891dd81f4b1ec80acca4191b127ee23b84654a12`
- Tracked files / lines: 55 / 10,597
- Declared license: MIT
- License SHA-256: `5c932d88256b4ab958f64a856fa48e8bd1f55bc1d96b8149c65689e0c61789d3`
- No submodules or local source modifications.

## Inventory and test adaptation

The frozen source contains 12 AVA test files and 339 textual `test(`
declarations. Its public root includes the asynchronous, synchronous, stream,
task-generation, dynamic-pattern, ignore-predicate, and path-conversion
families. The scored contract uses a JSON-only adapter, so stream and
predicate-returning APIs are documented as outside the fixed denominator.

The private deterministic slice contains 10 `node:test` leaves covering
positive and negated globs, directory expansion, negation-only behavior,
synchronous parity, task generation, dynamic-pattern detection, literal path
escaping, ignore-file filtering, and invalid-input errors. The test bundle and
adapter are private artifacts; no hidden test bytes are copied into the public
catalog.

## Runtime and dependency closure

- Agent/verifier runtime: Node `24.19.0`, npm `11.17.0`, linux/amd64,
  glibc, image digest
  `sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`.
- Candidate runtime dependencies: seven direct npm packages and their 23
  package closure, all resolved with integrity metadata and no native or
  platform-specific packages.
- Offline bundle digest:
  `sha256:f5765218e36e38ee460758c2cc5850d71f4959691d5dd71dac2a20b8c55ded62`
  (`586024` bytes). It contains only v3 `package-lock.json`, `npm-cache/`,
  and `bundle.manifest.json`; the bundle validator passed with npm 11.17.0.
- Clean `npm ci --offline --ignore-scripts --no-audit --no-fund` and
  `npm pack --ignore-scripts` passed in the pinned Node 24 image.

The upstream package has a GitHub devDependency and no lockfile. The authoring
remediation intentionally creates a reviewed runtime-only package manifest and
lockfile for the installable package; the scored contract does not require the
upstream AVA/XO development toolchain.

## Harbor and verifier evidence

- Private command bundle:
  `sha256:2638d4835f940fed1f9936bbab687e5d8c95b3c4f5dac23f4b308eaacb7f6eda`
  (`242` bytes).
- Private test bundle:
  `sha256:b2b49cc0703e07201925d36fd73c61e2c0ddad6ce15c452f9c7d47485139ca2f`
  (`1877` bytes).
- Oracle bundle:
  `sha256:5c4e45425a5a36c03d4d3a92a515fba066c0ff3ba82c60a8c66cdd25b7e06f77`
  (`78728` bytes). It carries the frozen source archive privately so the
  trusted Oracle does not require Git or a source-network exception.
- Agent and verifier network mode: `no-network`; no static allowlisted hosts.
- The separate Node verifier uses the locked subprocess candidate boundary,
  offline npm install, package-tar validation, fixed leaf collection, and
  verifier-owned `node-test-json-v1` grading.

The remediation recompiled the production bundle after restoring all four
declared private artifacts and adding task-local control scripts. Harbor
`0.21.0` then produced a valid Oracle result with reward `1.0` and `10/10`
leaves. Independent no-network controls produced empty `0.0`, stub `0.1`,
forgery `0.1`, call-hang `0.0`, and offline Oracle `1.0`; the verifier-owned
grading and network receipt paths are recorded in
`evidence/control-matrix.json`.

## Evidence commands

```text
git clone https://github.com/sindresorhus/globby .nl2repo/authoring-work/source/globby
git -C .nl2repo/authoring-work/source/globby checkout --detach 46cf13ff8bf5f0e0db96c4985faf83a59d194777
docker run --network none node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848 npm ci --offline --ignore-scripts --no-audit --no-fund
python /data/NL2RepoBench/scripts/check_agent_network_policy.py --task-root catalog/tasks/globby
python /data/NL2RepoBench/scripts/lint_authoring_task.py --task-root catalog/tasks/globby
```

An upstream `npm install --ignore-scripts` probe in the Node 24 image exited
`254` because the image lacks the `git` executable required by the source's
GitHub devDependency. The production Oracle therefore uses the privately
stored frozen source archive rather than Git checkout. This is an
environment/toolchain probe, not a source license or revision blocker; the
runtime-only offline closure above removes that non-runtime dependency and is
independently validated.

## Residual risks

- This is one Oracle run plus deterministic negative controls, not a
  cross-run stability experiment.
- The fixed denominator intentionally excludes stream and predicate-returning
  APIs because the current candidate client only transports JSON values.
- Full upstream AVA/XO/tsd parity is not claimed; this task is a bounded
  installable runtime slice.
