# p-timeout instruction revalidation blocker

## Classification

`artifact-or-verifier-blocked`: the frozen source archive is not available in
the trusted local inputs, while the only registered Oracle bundle contains a
`solve.sh` that fetches the revision from GitHub at runtime. Runtime source
fetch is forbidden by the task's NoNetwork contract. No fresh Oracle or control
receipt is claimed.

## Frozen inputs checked

- Queue source digest: `sha256:37c8ba48353a78b7aa4e18883614c7ff5895d3306bf25fb8ecf8b67a72e57b82`.
- Upstream revision: `245066ef7daa5e74024d5b6a188ae599a1b7bfdf`.
- Declared source archive: 40,960 bytes,
  `sha256:4f8e9a6fa4d0b1f3db355bfec23fe3fb646abdf062e112455a78bf756eeca151`.
- `validate-source` confirmed task `p-timeout`, version `2.0.0`, and the queue
  source digest before this evidence was written.
- The exact archive digest was searched in the current source and projection,
  private CAS, local authoring handoffs, historical catalog projections, and
  bounded archive/cache paths; no matching payload was found.

## Artifact verification

The dependency, command, and test bundles were present in the private CAS and
their exact bytes, sizes, and SHA-256 values are recorded in
`artifact-inventory.json`. The Oracle bundle was also present: it is a
10,240-byte bundle whose complete tar inventory is only `solve.sh`; it contains
no source payload. Its script uses the forbidden runtime GitHub fetch path.

## Revalidation decision

Do not compile or run Harbor with source-host authorization. A fresh Oracle
would either fail before source installation or violate the NoNetwork rule,
and existing pre-migration receipts are stale because the public instruction
bytes changed. Controls are skipped because no current final manifest and no
offline Oracle source payload exist.

## Remediation

Parent should recover an exact 40,960-byte archive matching
`sha256:4f8e9a6fa4d0b1f3db355bfec23fe3fb646abdf062e112455a78bf756eeca151`
from a trusted local backup, register it through the parent-only CAS flow,
replace the runtime-fetching Oracle payload, compile twice with the locked Node
toolchain, and run a complete fresh NoNetwork Oracle/control matrix. Do not
register a replacement proposal without independently proving archive bytes,
revision, and source digest.

## Commands and results

- `uv run nl2repo task validate-source catalog/sources/p-timeout` — exit 0.
- Exact private CAS `sha256sum` and `stat` checks — exit 0; all four declared
  private bundles matched their expected digest and size.
- Oracle bundle `tar -tf` inventory — exit 0; only `solve.sh` was present.
- Bounded local exact-digest payload search — exit 0; frozen source archive not
  found.
- Harbor compile, Oracle, and controls — not run; source payload and compliant
  Oracle are unavailable.
