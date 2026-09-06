# Instruction revalidation blocker

The instruction-migration queue expected source digest
`sha256:d18dc8531a11701dc1d94066093522c370f7169667e2ba64a984de8ef67f34bf`.
`nl2repo task validate-source` returned exactly that digest before this evidence
was added.

All three declared private artifacts exist in the parent CAS and match their
declared sizes and SHA-256 values. Two production compiles using
`toolchain.lock.toml`, `--allow-private`, and no `--allow-incomplete` were byte
identical. The migration-era manifest is
`sha256:2d0ba19f5bf74004479401416e0cee2492152bf836f642f1eeac9ea772fb96ab`
with canonical digest
`sha256:c696631df4d7357979746060c98e6e74541b8ba5359d81299ed35984889ac7f1`.

Revalidation cannot proceed under the required NoNetwork policy. The declared
Oracle bundle contains only `solve.sh`. That script performs `git clone` and
`git fetch` against `github.com`; it contains no source payload. The exact
frozen source is commit `17cb25eb7bc3556a68f3f7b241313e9bb8b23760`, whose
unprefixed git archive must hash to
`sha256:50b897e1c615278d8f9add946f74635564c500d01503793a0663f615eedf8622`.

A bounded offline search covered the checked-in runtime, task evidence,
retained authoring state and handoffs, read-only historical catalog copies,
local uv/pip caches, exact Git-object identity, and task-named Docker residue.
No archive or Git object satisfying both the revision and archive hash was
found. The only package-specific cache hit was an editable wheel containing a
`.pth` reference to the deleted original worktree; it contains no source bytes.

No Harbor trial was started, no source-host or registry authorization was
added, and no prior receipt was reused. `task.toml`, the migrated instruction,
lifecycle state, and `production-evidence.json` remain unchanged. The next
unblock action is for the parent to supply and register a private replacement
Oracle bundle containing the exact hash-verified source archive and an offline
`solve.sh`; the resulting source digest and manifest must then be recomputed,
followed by Oracle and the full supported control matrix.
