# fast-string-width instruction revalidation blocker

- Task: `fast-string-width`
- Revalidation date: `2026-09-05`
- Expected current catalog source digest: `sha256:b390d83b4bb6d7d7f7d8f25df14b1f695a28451dc0839dc136984fc82bb76c3e`
- Frozen upstream revision: `f49e7b7662906e0028a68a16b5358500b2f3152d`
- Frozen upstream archive digest: `sha256:352c8745134753593e770f0ffd8cb6e6ff2ef7f516b11ae56059f43e27d30698`
- Lifecycle: unchanged at `controls-passed`; this is an artifact/verifier revalidation blocker, not a lifecycle transition.

## Completed checks

`uv run nl2repo task validate-source catalog/sources/fast-string-width` passed and
reported the expected source digest. All four declared private artifacts were present
in the parent CAS and matched their declared sizes and SHA-256 values; see
`artifact-check.json`.

The current source was compiled twice with Harbor `0.21.0`,
`toolchain.node.lock.toml`, the parent private CAS, `--allow-private`, and no runtime
host authorization. Both production bundles contain 84 files and are byte-identical.
Their canonical manifest digest is
`sha256:702d91f6272b62a9ec363048736def0e0540b8f785cc0ef15b8e41ea32177489`, and the
bundle-manifest file SHA-256 is
`sha256:a988cebc8c360593124ddddad970b4dbb139516d020c1ba0f953c53dd8995fa9`.

## NoNetwork blocker

The hash-verified Oracle artifact contains `solve.sh`. Before creating the reference
package, that script adds the upstream GitHub URL as a remote and executes `git fetch`
for the pinned revision `f49e7b7662906e0028a68a16b5358500b2f3152d`. This violates the
required NoNetwork contract for Agent, candidate, verifier, Oracle, and controls.
The exact artifact and script hashes, source revision, and inspection result are
recorded in `oracle-bundle-summary.json`.

Harbor Oracle, empty, stub, forgery, and offline controls were not run. No run ID,
grading, collection, network, result, failure-set, or reward receipt is claimed;
`matrix-status.json` records this explicitly. Historical `production-evidence.json`
was left unchanged because its receipt paths are old `.nl2repo` run-tree paths and its
Oracle command authorizes GitHub.

## Remediation

Register a replacement private Oracle bundle containing a local, revision- and
archive-digest-verified source payload, or replace `solve.sh` with an equivalent
source-local immutable payload. Recompile twice against the replacement and run the
complete Harbor Oracle, empty, stub, forgery, and offline matrix without external host
authorization. Persist all new receipts under this evidence directory before updating
`production-evidence.json`; do not change the frozen denominator or lifecycle solely
because of this artifact/verifier blocker.
