# process-warning instruction revalidation

## Result

- Classification: `artifact-or-verifier-blocked`.
- The queue source digest was validated before mutation: `sha256:c24892c75fc0d6f4c76fee19eb7b71eab4146012a6462c39e9de7f5b09124a21`.
- The frozen upstream source remains known at revision `d55637b341e21fef9dc7222590b36b14d030a839`, archive digest `sha256:6ea9bf54d357fb67d7024510e082e37b59fea0516c32f3e0fdabc897fa9344a4`, with MIT license and denominator 24.
- All four declared private artifacts were found and verified by exact byte size and SHA-256. The Oracle bundle is present but contains only `solve.sh`; that script fetches `github.com` at runtime and does not contain the frozen source archive.
- Bounded trusted-local searches found no exact source archive matching the frozen digest. Historical projections and receipts were inspected but not reused because the instruction migration invalidated them.
- Compile, Oracle, and controls were skipped truthfully. No lifecycle, production evidence, generated projection, shared CAS, or private payload was changed.

## Remediation

Register an exact archive for the frozen revision through the parent-owned CAS workflow, or replace the Oracle payload with an auditable offline bundle whose internal archive matches the declared digest. Then compile twice with `toolchain.node.lock.toml` and run Harbor 0.21.0 Oracle plus every supported control with `network_mode=no-network` and no external host authorization.

See `commands.log`, `artifact-inventory.json`, and `blocker.json` for the bounded command record and exact artifact observations.
