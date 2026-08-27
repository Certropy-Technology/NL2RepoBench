# Luxon Authoring Provenance

Status: `awaiting-agent-run` for downstream Harbor model execution. The
declarative lifecycle remains `specified` because the shared lifecycle enum
has no `awaiting-agent-run` value. This lane did not start a model Agent Run.

## Candidate and source lock

- Source: `https://github.com/moment/luxon`
- Revision: `f427515a38f6a671f8de663e6bcc040ed81f114e`
- Commit tree: `56481e7b5540e011f616196154fd1d892c67bfb5`
- Commit subject: `Rewrite Duration#shiftTo and normalize to do less "unintuitive" conversions.`
- Source archive: `git archive --format=tar HEAD`
- Source archive size: `2,017,280` bytes
- Source archive SHA-256: `d7bffd1685fbefa37084674a85ce1a088dffa1fee775e58ac64604ff937bb939`
- License: MIT, from root `LICENSE.md`
- `LICENSE.md` SHA-256: `6cb2f2bf697ee9c6fa9eb8f227c63ee6e7a3cba42d4717f14c745ef9b6cbc006`
- `package.json` SHA-256: `8284e68bb4f286c77fb15d3227ed7e6d50a9de344e19af8a09128a4fade11818`

The checkout was detached at the full revision and has no submodules or local
source modifications. The source archive is retained only in the task-local
authoring work directory and is not exposed to a model Agent run.

## Runtime and source behavior

The package is Luxon `3.7.2`, with CommonJS and ESM exports. The source has 25
tracked files under `src/`, 60 tracked test files, and a committed npm v2 lock
with 1,052 package entries. The full upstream Jest suite contains 1,222 leaf
tests. It passes 1,222/1,222 under `TZ=America/New_York`, Node `22.23.1`, and
npm `10.9.8`; the host-default timezone causes known local-zone failures, so
the scored JSON contract uses explicit zones and a smaller deterministic leaf
set.

## Contract boundary

The private bridge invokes only public class/static/instance methods and maps
DateTime, Duration, Interval, and Zone values to JSON. It excludes host-clock
defaults, browser builds, callbacks, custom classes, direct Date objects,
functions, and the full upstream development suite. This is a deliberate
transport boundary, not a claim of complete in-process API parity.

The frozen verifier contract has 58 unique `node:test` leaves: 1 package
export leaf, 17 DateTime leaves, 14 Duration leaves, 19 Interval leaves, 4 Info
leaves, and 3 FixedOffsetZone leaves. The test implementation, bridge, command
plan, and traceability table are private CAS material and are not stored in the
public catalog source.

## Dependency policy

Luxon has no runtime dependencies. The candidate receives a root-only npm v3
lock and an empty npm cache closure, and installs with npm `11.17.0`
`npm ci --offline --ignore-scripts --no-audit --no-fund`. The upstream v2
development lock is used only for the authoring build and test probe; it is not
installed during evaluation.

## Evidence

Commands, package inventory, upstream test results, private bundle hashes,
compile output, and control receipts are recorded under `.nl2repo/authoring-work`,
`.nl2repo/harbor-jobs`, and the final `authoring-handoff.json`. Three upstream
baselines each passed 1,222/1,222 tests. The production verifier passed 58/58
with `valid=true` and reward 1.0; empty, stub, and forgery controls scored 0,
and the call-timeout control scored 1/58 while terminating within the bounded
timeout. The verifier network probe denied both a public IP and `pypi.org`.
