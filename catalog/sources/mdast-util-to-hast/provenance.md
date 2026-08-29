# Provenance

- Frozen upstream: `https://github.com/syntax-tree/mdast-util-to-hast`
- Revision: `174795b21f7757fffb54dd8d5fb4012f4751f791`
- Upstream package version: `13.2.1`
- License: MIT; `license` is included in the frozen git archive.
- Git archive command: `git archive --format=tar --prefix=mdast-util-to-hast/ HEAD`
- Git archive SHA-256: `587e4050147dc8730b15a6ceedd07866301c4309bcdf8856697bbb3ba96f7094`
- Upstream source-only probe: `npm run test-api`, Node `v22.23.1`, exit `0`, 142/142.
- Full upstream `npm test` probe: exit `1` at TypeScript checking because the
  floating dependency graph resolved a `null` type in `lib/handlers/image-reference.js`;
  this environment issue is retained as evidence and is not used as a production
  denominator.
- Production runtime: Node `24.19.0`, npm `11.17.0`, Debian Bookworm amd64,
  digest-pinned base image from `toolchain.node.lock.toml`.
- Candidate dependency closure: no third-party runtime packages; the private npm
  bundle contains the v3 lock and a content-addressed npm cache closure for the
  seven declared runtime packages; lifecycle scripts are disabled.
- The private JSON child contract collected 35 leaves. The frozen upstream
  `npm run test-api` baseline collected 142 and passed 142, but the production
  denominator deliberately covers only the documented JSON-safe API boundary.
- Harbor 0.21.0 production Oracle and offline replay each passed 35/35 with
  `public_network_available=false`. Empty and install-script controls stopped at
  candidate installation; stub, forgery, and loader-hook remained low-score; the
  call-hang and timeout controls were bounded by the child supervisor.
