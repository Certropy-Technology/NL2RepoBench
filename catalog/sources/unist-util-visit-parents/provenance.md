# Authoring Provenance

- Task: `unist-util-visit-parents`
- Upstream: `https://github.com/syntax-tree/unist-util-visit-parents`
- Revision: `f06035e9161f25119fb68d178167c30003d32dfb`
- Git tree: `89b75582183bf6030d9f75144b3d2dedbef425bf`
- Package/tag: `unist-util-visit-parents@6.0.2`
- License: MIT; frozen `license` SHA-256
  `ca4662cb5d1b738fbe5350c0d5485ba11773b4b7208974082ae6e129a52d631d`
- Git archive: 71,680 bytes; SHA-256
  `39843fba2b73f69a59ca59e06cf646ad20c2999f4c3e2ac75b427e80f8e5d066`
- Runtime: digest-pinned Node `24.19.0`, npm `11.17.0`, Debian bookworm,
  `linux/amd64`, glibc 2.36
- npm closure: exact `@types/unist@3.0.3` and `unist-util-is@6.0.1`, v3
  lock, no native/install-script packages, private artifact SHA-256
  `0309d9df7a84fc955ad0985406796c99a3b1412c546d8daf99aaed27442d23d0`
- Private verifier: 50 flat `node:test` leaves, private artifact SHA-256
  `9fdf5fa48036e31027c054c101f54855ccec6d79200fd5bfba46925233535627`
- Oracle bundle: exact-revision fetch, commit/archive assertion, packaging-only
  metadata normalization, and frozen lock; private artifact SHA-256
  `5fe42af2fa5e2ab635c00dabf0bf8698ac4825b9a44e3691b7fb262911c78a8f`

Inside the pinned Node image, the frozen upstream source completed `npm run
build` with 780/780 covered type expressions and `npm run test-api` with 24/24
behavioral leaves. A clean no-network cache replay installed the exact two-node
runtime closure. The UID-separated private verifier then passed 50/50 against
the packaging-normalized frozen source with Docker network mode `none`.

Production compile, official Harbor Oracle, and control receipts are recorded
after those gates run. No model Agent Run is permitted in this lane.
