# `aiohttp` authoring audit - blocked

**Status: blocked / audit-only.** This source record is not a runnable task,
public implementation specification, verifier, Oracle, or Harbor projection.
No `catalog/tasks/aiohttp/` runtime should exist while this blocker remains.

## Assigned Source

- Upstream: `https://github.com/aio-libs/aiohttp`
- Assigned revision: `25522ad29937a6b586cb4dbe906c96db45fdc672`
- Required execution policy: `network_mode=no-network` for the Agent,
  candidate, verifier, Oracle, and every control.

The source authority could not be established. A bounded authoring-only
`git ls-remote` found no matching advertised ref. An exact shallow fetch of the
assigned object exited 128 with `upload-pack: not our ref`, and the object is
not present in the local repository after that attempt. Therefore no source
archive digest, license bytes, dependency closure, test denominator, verifier,
or Oracle payload can truthfully be bound to this revision.

The prior aiohttp authoring attempt is not reusable: its checkout is at a
different commit and does not contain the assigned object. Its observations
about native HTTP parsers, asynchronous client/server state, callbacks,
WebSockets, and socket-oriented tests remain supportability risks, but they are
not treated as evidence for this unavailable revision.

## NoNetwork Boundary

No runtime command was attempted. No GitHub, PyPI, package-index, TLS, socket,
or external-service access is permitted during Agent, candidate, verifier,
Oracle, or control execution. No private artifact reference is declared
because no artifact was created from the unavailable source.

## Remediation

1. Correct the discovery record to a complete commit that belongs to the
   declared upstream, or provide authoritative proof and an immutable source
   object for the assigned revision.
2. Freeze that exact object and verify its archive and license digests.
3. Freeze the complete hash-locked build/test closure before any runtime.
4. Reassess a child-side adapter that does not use runtime network/TLS services
   and does not let trusted pytest import the candidate.
5. Only then define a positive frozen denominator, build private verifier and
   Oracle bundles, compile, and run the NoNetwork Oracle and controls.

Until all five steps succeed, lifecycle remains `blocked` and no reward is
reported.
