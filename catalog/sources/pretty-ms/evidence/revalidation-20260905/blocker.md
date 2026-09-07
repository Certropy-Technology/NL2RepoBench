# pretty-ms instruction revalidation blocker

Classification: `artifact-or-verifier-blocked` (source payload unavailable for an
offline Oracle). This is not a candidate or model result.

## Frozen inputs checked

- Queue source digest: `sha256:29ace9e50cca75e857a371f7b2c2645d5410d0ae9c070860f4cde2f0c6232c32`.
- `uv run nl2repo task validate-source catalog/sources/pretty-ms`: exit `0`; the
  source digest matched the queue entry before this evidence was written.
- Declared npm bundle: `sha256:fc8df9226bacdd04ae3fb969befb3d24cc63aec9d26ea12d3a483bcbff73acf8`,
  `11250` bytes; CAS bytes matched both size and SHA-256.
- Declared command bundle: `sha256:3a0d5d438bfa114938040770c8c288320518bdaec8733dbd7f373f0c5cf0827f`,
  `261` bytes; CAS bytes matched both size and SHA-256.
- Declared test bundle: `sha256:086f2a56063eec10d873105ac49705aa463144807b46cc9fc5b7db0a85e8ded9`,
  `1738` bytes; CAS bytes matched both size and SHA-256.
- Declared Oracle bundle: `sha256:567d800c5272f7f9bbfe347980ae9688156eebc09783922ed648e77245e674dc`,
  `1122` bytes; CAS bytes matched both size and SHA-256.

The frozen Oracle bundle was inspected. Its `solve.sh` fetches the revision from
GitHub at runtime and therefore cannot run under the required no-network Oracle
policy unless an exact frozen source archive is supplied separately. The declared
source archive digest is `sha256:e2a108dc70512373b94d959c2084d44eef117e32091a43659705375986408dd4`
(`51200` bytes).

## Bounded recovery

The current generated projection and local task source were inspected, followed by
a bounded local search of trusted `.nl2repo` payloads for a 51200-byte archive with
the frozen source digest. The search timed out without producing a matching path;
no replacement payload is proposed. Historical handoff/projection copies were
treated as stale and were not used as receipts or source authority.

Commands and normalized logs are recorded in `command-results.json` and
`recovery-search.log` in this directory. No Oracle, control, projection, lifecycle,
or production-evidence claim was changed.

## Skipped gates and unblock action

Skipped: compile-final-manifest, fresh Harbor Oracle, empty, stub, forgery, offline,
and source/projection acceptance. Running these without the exact source payload
would either reuse a stale receipt or permit the forbidden runtime GitHub fetch.

Next step: recover or parent-register an exact 51200-byte archive whose SHA-256 is
`sha256:e2a108dc70512373b94d959c2084d44eef117e32091a43659705375986408dd`, then
compile twice with the locked Node toolchain and run a fresh no-network Harbor
Oracle plus all supported controls. Keep the lifecycle and historical evidence
unchanged until those gates complete.
