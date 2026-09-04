# multidict authoring audit

## Source freeze

- Upstream: `https://github.com/aio-libs/multidict`
- Revision: `86351873dcc36edb11ba1a27035f2ce2e9ff8f4e`
- Git tree: `147384c1581879b427a08239180ebe08e7051c9d`
- Exact `git archive --format=tar HEAD` SHA-256: `sha256:bfdff853c97ee413df6bde23098fbef8d6232dec8c4a2a9c2dd6a26dbd93040d`
- License: Apache-2.0; `LICENSE` SHA-256: `sha256:2e4be5fc6c4c72a466fcb665d726e049a6891981fe536c4f04b6366749461d23`
- Upstream package version at this revision: `6.7.2.dev0`
- No submodules.

## Environment and dependency closure

The package ships a C implementation but selects its bundled pure-Python implementation when `MULTIDICT_NO_EXTENSIONS=1`. The authoring probe installed the pinned source with `setuptools==84.0.0`; runtime has no third-party dependency. The build lock and private verifier/oracle bundles are stored in the assigned external handoff directory and referenced only by opaque digest in the source manifest.

All Harbor Agent, candidate, verifier, Oracle, and control execution is `network_mode=no-network`. The Oracle restores a digest-checked source archive rather than fetching upstream at runtime.

## Verifier boundary

The trusted verifier stages its adapter to a temporary path and invokes it as the candidate UID with bounded resource limits and isolated import paths. Candidate code cannot write trusted grading or reward reports. The verifier compares JSON-safe projections and creates the fixed-denominator report.

## Risks and exclusions

The task does not require native compilation, pickle compatibility, memory leak behavior, benchmark timing, or C-extension-only crash guards. Those behaviors are outside the stable JSON subprocess contract. A pure-Python implementation remains faithful to the documented public API.
