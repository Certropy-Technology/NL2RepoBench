# p-retry instruction revalidation

## Frozen inputs

- Queue entry: task `p-retry`, queue position 198.
- Source digest verified before mutation: `sha256:74d4571907395aa0a316f47a888a4b200b2570802e527ef4bb84ed91b5022856`.
- Instruction digest: `sha256:ba56f7a66e124179ca376ab514e8d2b17a1bc5c5e9be81af338964ad9923de1a`.
- Upstream revision: `35681f6c70f8ca2bdcb9542281147679184269fa`.
- Frozen source archive: 81,920 bytes, `sha256:3eabac5b48586a9a65714ad4cc4685a03705e3adcf3ee57d7ce9dabf5beb8278`.
- Frozen denominator: 46 node-test leaves.

## Local artifact verification

The four declared private artifacts were found in the trusted local CAS and each
matched both declared size and SHA-256. Exact details are in
`artifact-inventory.json`. No CAS bytes were changed.

The bounded recovery scan examined 47,217 files across trusted local CAS,
historical handoffs, generated projections, and task-local source. Seven files
had the frozen 81,920-byte size; none matched the frozen archive digest.

## Classification

`artifact-or-verifier-blocked` — the only Oracle payload is a runtime
`git fetch` from `github.com` followed by an archive digest check. No exact
frozen source archive is locally available, so an Oracle or control run cannot
be performed under the required `network_mode=no-network` policy. Existing
production evidence remains historical and is not reused as current evidence.

## Gate state

- Source digest and source declaration validation: passed.
- Private artifact size/SHA-256 checks: passed for 4/4.
- Exact frozen source recovery: failed; 0 exact matches.
- Compile twice: skipped because the source/oracle artifact closure cannot be
  made complete without changing unregistered private inputs.
- Fresh Harbor 0.21.0 Oracle: skipped; runtime source fetch is forbidden.
- Empty, stub, forgery, install-script, loader-hook, timeout, and offline
  controls: skipped because no current final manifest and Oracle source payload
  are available.

## Remediation

Parent should recover or register an exact archive whose bytes match the frozen
source digest, replace the fetch-only Oracle payload with a digest-bound local
payload, compile twice using the locked Node toolchain, and rerun the complete
NoNetwork Oracle/control matrix. Do not alter the frozen denominator or reuse
the historical receipts.
