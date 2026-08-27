# Ramda Authoring Provenance

Status: packaged pending Harbor Oracle and control gates.

- Upstream: `https://github.com/ramda/ramda`
- Revision: `803cab30f2e63cd102c6721c1da6c61e57e12429`
- Commit tree: `6c4cde85cbe0609f233cfc328bb325ae4f4ead92`
- Commit date: `2026-07-26`; subject: `docs: clarify unionWith keeps the first equal item (#3536)`
- License: `MIT`, from `package.json` and tracked `LICENSE.txt`.
- Source archive command: `git archive --format=tar 803cab30f2e63cd102c6721c1da6c61e57e12429`
- Source archive SHA-256: `822decf848e9ef50edeca8b0f5f2e595abc18e643634d316a1f8addb5499b672`.
- No submodules were reported by the detached checkout.

The tracked project holds ESM modules in `source/`; CommonJS `src/` is created
by `npm run build:cjs`. The authoring baseline used Node `22.23.1`/npm `10.9.8`
to run `npm ci --ignore-scripts --no-audit --no-fund`, `npm run build:cjs`, and
the Mocha specification command. Three independent specification runs passed
`1215` tests, and the latter two transcript digests both equal
`098399a9a8b7fe909dbe1f70f6517c0de08283eb198a7464b28776be192ebc86`.

Static inventory found 369 tracked JavaScript source modules, 279 tracked
JavaScript test files, and 272 named default re-exports in `source/index.js`.
The bounded task contract selects 71 JSON-callable named functions from that
public root surface; callback, executable-object, currying, placeholder,
transducer, and non-JSON behavior is explicitly excluded rather than silently
left untested.

The scored package is a dependency-free CommonJS distribution built from that
frozen source. The private Oracle bundle verifies both the frozen source
archive and the distribution archive before copying only the distribution into
the Oracle workspace. Candidate installation requires a v3 lockfile and an
empty, integrity-checked npm cache closure with scripts disabled.
