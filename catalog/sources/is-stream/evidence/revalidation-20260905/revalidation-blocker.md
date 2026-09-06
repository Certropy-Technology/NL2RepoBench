# Revalidation Pending Parent CAS Registration

The declared private dependency, command-plan, test, and Oracle artifacts were
all present and passed their declared SHA-256 and size checks. The current
Oracle bundle cannot be used for this revalidation because its `solve.sh`
performs a runtime `git fetch` from the upstream source host, which violates
the required NoNetwork Oracle policy.

A deterministic no-fetch replacement proposal was constructed from the
hash-verified current Oracle payload. Its outer digest, complete inner file
digests, source-authority limitations, and direct Docker `network=none` smoke
results are recorded in `oracle-replacement-proposal.json` and
`no-network-smoke.json`.

The local npm cache provided a byte-level cross-check for the published package
files but cannot independently establish the frozen Git revision: its packument
records a different `gitHead`. The exact prefixed Git archive declared by the
task was not found in the bounded trusted-local search. Therefore this worker
did not edit `task.toml`, compile a stale manifest, or run Harbor. The parent
must verify/register the proposed private bundle, decide the provenance issue,
update the private artifact binding if accepted, then recompile twice and run
the full Oracle/control matrix against the changed final manifest.
