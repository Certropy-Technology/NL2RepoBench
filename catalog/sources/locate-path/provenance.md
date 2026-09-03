# `locate-path` Authoring Provenance

## Source and license freeze

- Upstream: `https://github.com/sindresorhus/locate-path`
- Frozen revision: `4c4ee027b830c35ff7605421a8ad92208f1b868a` (`v8.0.0`)
- Source tree: `4da63bfebadeaad61d829f358e16561f50815891`
- Unprefixed git archive: 30,720 bytes,
  `sha256:e5bf56cf0d89d2f6a1191cfea63f77157060ed42dcb3dcedc738de54595103bb`
- License: MIT; license bytes SHA-256
  `5c932d88256b4ab958f64a856fa48e8bd1f55bc1d96b8149c65689e0c61789d3`

The revision was resolved with `git ls-remote` and detached checkout. The
archive digest was recomputed locally. The complete upstream command
`npm test` passed on Node `22.23.1` / npm `10.9.8`, with XO, AVA (2/2), and tsd
all exiting zero.

## Runtime closure

The production candidate installs a runtime-only manifest with
`p-locate@6.0.0`, `p-limit@4.0.0`, and `yocto-queue@1.2.2`. The npm v3 lock has
integrity values for all package entries, and the private cache bundle contains
only `package-lock.json`, `bundle.manifest.json`, and npm cache files. The
bundle validator and a fresh Docker `--network none` `npm ci --offline
--ignore-scripts --no-audit --no-fund` smoke both pass on the pinned Node 24
image.

## Verifier boundary

The private bundle contains `contract.test.mjs`, `test_client.mjs`, and a
candidate adapter. It never imports candidate code into the trusted process.
The adapter constructs a bounded temporary filesystem tree and returns only
JSON-safe path results or error constructor/message pairs. The Oracle bundle
fetches the frozen revision only inside the trusted Oracle run, verifies the
resolved commit and archive digest, and installs the runtime-only manifest.

The source-local work directory and CAS paths are recorded in the handoff;
large source, cache, test, and Oracle bytes are intentionally outside the
public catalog source.
