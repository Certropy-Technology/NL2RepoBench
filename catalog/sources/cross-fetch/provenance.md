# `cross-fetch` Authoring Provenance

## Frozen source

- Upstream: `https://github.com/lquixada/cross-fetch`
- Revision: `9e6898ee848ba6dc942f787f2c35ca6fa30eb014`
- License: MIT; `LICENSE` SHA-256:
  `821a6be45c3fd08815688b30b6210fc97848cf88c7a6ed8afb22ae75b83571b4`.
- Exact archive command: `git archive --format=tar <revision> | sha256sum`.
- Exact archive SHA-256:
  `2924f22280494620dfee8fd974a0a85f6668334b16eed7b540b7fe4d24706491`.
- No submodules.

The source package declares `cross-fetch@4.1.0`, `main` as
`dist/node-ponyfill.js`, and a `node-fetch` runtime dependency. Its source
suite spans Node, browser, React Native, and service-worker environments. This
task retains only the deterministic Node ponyfill subset.

## Offline closure

The private npm v3 lock/cache closure pins `node-fetch@2.7.0` and its exact
transitive packages. It was generated with lifecycle scripts disabled and is
installed during image build. Candidate and verifier execution remain offline.

## Verifier scope

The private `node:test` adapter contains 22 fixed leaves. It creates a
verifier-owned loopback server for the single fetch round trip, executes the
candidate under UID 10001, and exchanges only JSON-shaped fixed operations
with a bounded child bridge. Trusted verifier code never imports the candidate
package directly.
