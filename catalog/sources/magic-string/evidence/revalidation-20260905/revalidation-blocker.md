# magic-string revalidation blocker

- Task: `magic-string` version `2.0.0`
- Queue source digest: `sha256:f3156d9d1406de2215414cbce452b745c5bf4b099d22da15dd71fa9eca3ea8d7`
- Frozen upstream revision: `5473bfb5138e7b7c2fc91d964c0425f57f1470ce`
- Frozen source archive digest: `sha256:1b3e623bb3bb86c83379df039c375108a2b468fecc4bcaf6ff02d3ee89275503`
- Classification: artifact-path blocker; lifecycle and historical production evidence unchanged.

## Checks

`validate-source` passed before mutation. All four declared private artifacts were
found in the parent CAS and matched their declared sizes and SHA-256 values; see
`artifact-check.json`. The Oracle bundle includes the exact 460800-byte source
archive, whose digest matches the frozen source digest. Its `solve.sh` contains no
runtime source fetch or network command; see `oracle-payload.json`.

The source compiled twice with the locked Node/npm toolchain and parent CAS. Both
`bundle.manifest.json` files were byte-identical (raw SHA-256
`sha256:29dd6887994bf927886dccd147fda612e6a611636bb54b49bacc27b317d62543`,
canonical digest `sha256:14039f6e75ffb3af22b5bc1b7f96837d635e48b2dbf5a289cda51c67ff888c1d`).
However, the generated npm cache contains a debug log with absolute authoring
worktree paths under the cache log and configuration records. This violates
projection artifact hygiene, so no Harbor Oracle or control receipt was created or
reused.

## Remediation

Rebuild the npm dependency cache without debug logs or authoring-worktree metadata,
register the normalized bytes in the parent CAS, compile twice again, and rerun the
complete fresh NoNetwork Oracle/control matrix. Do not alter the denominator,
lifecycle, or historical production evidence to bypass this blocker.
