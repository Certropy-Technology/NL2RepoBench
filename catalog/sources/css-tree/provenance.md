# CSS Tree Authoring Provenance

## Immutable source and license

- Upstream: `https://github.com/csstree/csstree`
- Revision: `88e3d965c0b1628642a30a841745b410d6835052`
- Commit subject: `Add note about stacked multipliers`
- Commit tree: `c86ba0a6861540cc9e4ae1375e4f63fe14c1d25d`
- Git archive command: `git archive --format=tar <revision>`
- Git archive SHA-256: `8b568680478944896703c6bc412665f5abb0720efe9f39372d3cb66ffa7ad778`
- Codeload archive SHA-256: `4223c7a31191c6117f6ad21b40a5e391c1d130da85e2cfe482ef2c38bccf0dea`
- License: MIT; `LICENSE` SHA-256 `719a251ceca49c057ea90a1152af6546b767ec88e6d573bb6324454267b32c22`
- `package.json` SHA-256 `bd734f2de92e7a254bd05970fa83b30f8be9ed73e33577065a1529e59843cfd4`

The exact SHA was resolved with `git ls-remote`, fetched without tags, and
checked against both the git object and codeload archive. The codeload digest
is checked again by the trusted Oracle solution before extraction.

## Baseline and environment

The authoring probes used Node `22.23.1`/npm `10.9.8` on Fedora x86_64. The
production lock selects Node `24.19.0`/npm `11.17.0`, Debian bookworm,
linux/amd64, glibc, and base image
`docker.io/library/node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`.
`npm ci --ignore-scripts` installed 185 packages. The upstream command
`npm test` collected 16,727 cases, passed 16,725, and left 2 pending. The
complete `npm run build-and-test` command passed, including generated dist and
CJS checks.

## Runtime dependency closure

The frozen package declares exactly two runtime roots: `mdn-data@2.27.1` and
`source-map-js@^1.2.1`; both have no runtime transitive dependencies. The
production artifact is generated as an npm v3 lock/cache bundle for npm
`11.17.0`, with integrity metadata and lifecycle scripts ignored. Development
dependencies such as Mocha, Rollup, esbuild, and ESLint are not installed in
the candidate verifier.

## Oracle adaptation

The private Oracle solution fetches only the codeload archive for the exact
revision, verifies the archive digest and a source-file manifest, and copies
the upstream `lib/` runtime plus license/readme into `/workspace`. It writes a
scripts-free package manifest and the production npm v3 lock. The source host
is authorized only for the trusted Oracle run; candidate and verifier phases
remain network-isolated.

## Boundary and exclusions

The candidate is exercised through a per-request JSONL child process. ASTs are
converted with `toPlainObject`; tokenizer callbacks become token records; walk
and find predicates are allowlisted by node type. Native objects, callbacks,
source maps, terminal state, browser bundles, CLI tools, and mutable stream
internals are excluded from the denominator. These are bounded adaptations of
the public API, not a claim of full upstream parity.
