# Email-validator instruction revalidation blocker

## Verified inputs

- Current catalog source digest: `sha256:101661beb1249f38b1fa643d27146a4f26e26077d5e9352b875ba8bed89ace5e`.
- Frozen upstream archive digest: `sha256:6645b1719e7183f35d0ec20900e67391d0a3c2d570f442957203d64758609801`.
- Harbor: `0.21.0`; runtime: Python 3.12; network policy: `no-network`.
- Fixed collection denominator: 30 pytest leaves.
- All declared private dependency, verifier, and Oracle artifacts were present and matched their declared size and SHA-256.

## Deterministic compile

The source was compiled twice with the locked Python toolchain, the parent private
CAS, `--allow-private`, and no runtime network authorization. Both commands exited
zero and the complete output trees were byte-identical.

- Canonical manifest digest: `sha256:b5175bbe14b282da28bb921ae4c457b4bdd68e80bf3bfa1583447cde152499bb`.
- Tracked bundle manifest: `bundle-manifest.json`.
- Tracked bundle manifest SHA-256: `sha256:827de16b7821670198fedc4d1e6fa59ce4e877beeef67c2f284b5c1c34865978`.
- Bundle file count: 58, including `controls/empty.sh`, `controls/stub.sh`, `controls/forgery.sh`, and `controls/install-hang.sh`.

## Revalidation blocker

The frozen Oracle payload contains only `solution/solve.sh`. That script performs a
runtime `git fetch` from the upstream GitHub source host before creating the archive.
Its payload SHA-256 is `sha256:f5576dbabd237dd03b4ae43c888b7514f6efcc1b512e9ce41f80028fc9f3b764`,
and the extracted solver SHA-256 is
`sha256:ba318eeaf8f8a1ec8742f7ebddabba9559a367ec6e5f7afd7867aef7662bb780`.

The required NoNetwork Oracle run was not started. Empty, stub, forgery, and offline
controls were also not run, because doing so against this payload would either require
forbidden source-host authorization or validate a stale/non-current Oracle bundle.
No current reward, collection, network, or failure-set result is claimed. The explicit
not-run summaries are tracked beside this record.

## Remediation

Register a local Oracle payload containing the exact frozen archive, verify the archive
against the source digest, compile the source again, and run one NoNetwork Oracle plus
the complete empty/stub/forgery/offline matrix. Do not authorize GitHub, reuse the old
receipts, lower the denominator, or change lifecycle and historical production evidence.
