# node-fetch instruction revalidation — infrastructure blocker

Date: 2026-09-07

## Scope and frozen inputs

- Task: `node-fetch` version `2.0.0`.
- Upstream revision: `8b3320d2a7c07bce4afc6b2bf6c3bbddda85b01f`.
- Frozen source archive digest: `sha256:c54ad1e222b0dab09410542e9142b5374a63a72b2e5cc8e931b147559628265c`.
- Frozen test denominator: 23 node:test leaves.
- Network policy: `no-network`; reference-source fetch is forbidden.
- All four declared private CAS artifacts were found and matched their declared size and SHA-256. The Oracle bundle contains a byte-identical 64-member source archive and a solve script with no source-fetch/network command.

## Compilation

The current source was compiled twice with `toolchain.node.lock.toml`, the parent private CAS, `--allow-private`, and without `--allow-incomplete`. Both output manifests were byte-identical:

- Raw checked-in manifest SHA-256: `sha256:57a5fd070f61f98ea2f7cf51b047470d5e0d03601ed55f55a191bb21b6ab5229`.
- Canonical manifest digest: `sha256:42332892b91bf47fee1b73c211a75ce8cd10b02b75a1ddd9edebafe1b159eefa`.

## Harbor execution

The first official Harbor 0.21.0 Oracle invocation failed before job creation with `Docker daemon is not running`. One bounded same-configuration retry was allowed. The retry reached a trial and then timed out after 300 seconds while collecting main-service artifacts; it produced no completed Oracle/verifier result. This is classified as `infrastructure`, not candidate/model failure.

Consequently, Oracle, empty, stub, forgery, timeout, and fresh network receipts were not completed in this revalidation. No score, valid result, or control pass is claimed here. The registered `offline` control kind is not available in the Node control registry because the compiled task has no `controls/offline.sh`; no substitute result is claimed.

## Durable raw logs

- `oracle-initial.log` records the first invocation failure.
- `oracle-retry.log` records the bounded retry outcome.
- The full ignored run tree remains under `<ignored-run-root>` for parent-side inspection and is intentionally not copied into the source catalog.

## Next step

Repeat the official Oracle and declared controls only after Docker is healthy, using this exact compiled manifest and fresh run roots. Do not reuse any prior receipt after subsequent source, instruction, compiler, manifest, or control changes.
