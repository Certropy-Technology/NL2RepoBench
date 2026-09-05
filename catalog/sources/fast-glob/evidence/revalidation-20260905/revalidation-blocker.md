# `fast-glob` instruction-migration revalidation blocker

- Task: `fast-glob`
- Revalidation date: `2026-09-05`
- Expected catalog source digest: `sha256:7dbdc5c8040f1808ca6e30b81b13066199d001764d13ef475d25a9326fb90f54`
- Lifecycle: unchanged at `controls-passed`.
- Historical `production-evidence.json`: unchanged. Its receipts are not replaced
  by this blocker record.
- Network policy: `no-network` for agent, candidate, verifier, Oracle, and controls.

## Offline checks

`uv run nl2repo task validate-source catalog/sources/fast-glob` passed and reported
the expected source digest. Harbor `0.21.0` was verified with
`uv run --frozen --project harbor-runner harbor --version`.

The four private artifacts declared by the source were checked only at the local
content-addressed CAS paths below. Every object is absent; no registry, GitHub,
codeload, DNS, source host, or external service was contacted.

| Artifact | Expected digest | Local CAS path | Result |
| --- | --- | --- | --- |
| npm dependency closure | `sha256:4ff767f70cfda06d60fbd4e9ee866c75437de276004a049c2925041101e9ca0b` | `.nl2repo/artifacts/private/sha256/4f/4ff767f70cfda06d60fbd4e9ee866c75437de276004a049c2925041101e9ca0b` | missing |
| Node test bundle | `sha256:56428100ac69806e55c009c8465c530d88dd3021637e8a33dc4c8d21793e5854` | `.nl2repo/artifacts/private/sha256/56/56428100ac69806e55c009c8465c530d88dd3021637e8a33dc4c8d21793e5854` | missing |
| Node command plan | `sha256:ae0d5dc22c9d5bf46ee967a7fffef897063c31a78046afc47d753287d5a61081` | `.nl2repo/artifacts/private/sha256/ae/ae0d5dc22c9d5bf46ee967a7fffef897063c31a78046afc47d753287d5a61081` | missing |
| Oracle bundle | `sha256:e448c9fec7a1a8809a6ec6dda68be55673e54cca44f391a770b6beceaa8558d0` | `.nl2repo/artifacts/private/sha256/e4/e448c9fec7a1a8809a6ec6dda68be55673e54cca44f391a770b6beceaa8558d0` | missing |

## Not run

Compilation, deterministic byte comparison, Oracle, empty, stub, forgery, and
offline Harbor controls were not run because the required private dependency,
test, command-plan, and Oracle artifacts are unavailable. No new grading,
collection, result, or reward is claimed. The checked-in generated task and
historical receipts remain untouched.

## Remediation

Register or restore all four private CAS objects with the declared digest and
size, then re-run `validate-source`, production compilation twice with the
locked Node toolchain and `--allow-private`, and require byte identity. Inspect
the Oracle payload for a local, revision- and source-digest-verified materializer
before executing it. Only after that should the complete NoNetwork Oracle,
empty, stub, forgery, and offline matrix be run and its compact, durable receipts
written under this evidence directory. Do not authorize external hosts, change
the frozen denominator, reuse the historical receipts, or change lifecycle state
solely because this infrastructure artifact blocker remains.
